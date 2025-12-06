from typing import Dict, Any, Union, List
from fastapi import FastAPI, HTTPException, Body
from src.services.retrievers import get_mock_data
from src.services.parallel_report_generator import ParallelReportGenerator
from src.models.report_schema import get_report_schema
from src.file_operations.load_email_marketing_data import SupportingDataLoader
from src.services.email_service import EmailService
import asyncio
import re
import unicodedata
import httpx
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Report Generation API")

@app.get("/")
def root():
    return {"message": "✅ Report Generation API is running"}

@app.post("/generate_report")
async def generate_report_endpoint(context_data: Dict[str, Any] = Body(...)):
    try:
        # Get metadata from context first to determine report type
        metadata = {}
        report_type = ""  # Extract report_type from metadata
        if isinstance(context_data, dict):
            # If metadata is directly in the context
            if "metadata" in context_data:
                metadata = context_data["metadata"]
                report_type = str(metadata.get("reportType", ""))
            # For backward compatibility - convert old filterValue structure
            elif "filterValue" in context_data:
                filter_data = context_data["filterValue"]
                report_type = str(filter_data.get("reportType", ""))
                metadata = {
                    "reportType": report_type,
                    "period": str(filter_data.get("period", "")),
                    "dateRange": {
                        "startDate": "",
                        "endDate": ""
                    },
                    "recordCount": 0
                }

        # Normalize report type to accept many input variants
        from src.services.report_types import normalize_report_type
        canonical_report_type = normalize_report_type(report_type)

        # Load report structure based on canonical report type
        structure = get_report_schema(canonical_report_type).dict()

        # Initialize parallel report generator
        generator = ParallelReportGenerator()

        # Generate reports using multiple LLMs
        reports = await generator.generate_reports(structure, context_data)

        # Create a map of tag IDs to their proper titles from the report structure
        title_map = {}
        for page in structure.get("pages", []):
            for tag in page.get("tags", []):
                if tag.get("title") and tag.get("id"):
                    title_map[tag["id"]] = tag["title"]

        # Handle different report types with specific logic
        if canonical_report_type == "retail-data":
            print(f"Processing retail data report (type: {canonical_report_type})")
            # Add retail-specific processing logic here
        elif canonical_report_type == "all-categories":
            print(f"Processing all categories report (type: {canonical_report_type})")
            # Add comprehensive data processing logic here
        elif canonical_report_type == "email-performance-data":
            print(f"Processing email performance report (type: {canonical_report_type})")
            # Add email-specific processing logic here
        elif canonical_report_type == "social-media-data":
            print(f"Processing social media data report (type: {canonical_report_type})")
            # Add social media-specific processing logic here
        else:
            print(f"Processing report with unknown type: '{canonical_report_type}' - using default logic")
            # Add default processing logic here

        def _normalize_text(s) -> str:
            if not s:
                return ""
            if isinstance(s, list):
                # For lists, normalize each item and join with newlines
                return "\n".join(_normalize_text(item) for item in s)
            # Convert to string if not already
            s = str(s)
            s2 = unicodedata.normalize('NFKC', s)
            s2 = s2.replace('\u00A0', ' ')
            s2 = re.sub(r"\s+", ' ', s2)
            return s2.strip().lower()

        # Create flat data structure organized by sources
        flat_data = {}
        for report in reports:
            source = report["source"]
            for page in report["report"]["pages"]:
                for tag in page["tags"]:
                    tag_id = str(tag["id"])
                    title = title_map.get(tag_id, tag_id)
                    
                    if tag_id not in flat_data:
                        flat_data[tag_id] = {
                            "id": tag_id,
                            "title": title,
                            "sources": {}
                        }
                    
                    if tag.get("content"):
                        content = tag["content"]
                        data = ""
                        try:
                            if isinstance(content, list) and len(content) > 0:
                                item = content[0]
                                if isinstance(item, dict):
                                    data = item.get("data", "")
                                elif isinstance(item, str):
                                    try:
                                        import json
                                        parsed = json.loads(item)
                                        if isinstance(parsed, dict):
                                            data = parsed.get("data", "")
                                        elif isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                                            data = parsed[0].get("data", "")
                                    except json.JSONDecodeError:
                                        data = item
                                else:
                                    data = str(item)
                            else:
                                data = str(content)
                        except Exception:
                            data = ""
                        
                        # Normalize data for deduplication
                        norm_data = _normalize_text(str(data))
                        if source not in flat_data[tag_id]["sources"] or not _normalize_text(flat_data[tag_id]["sources"][source]):
                            flat_data[tag_id]["sources"][source] = data

        # Transform flat_data into the final response format
        response = {
            "items": [
                {
                    "id": item_data["id"],
                    "title": item_data["title"],
                    "content": [
                        {
                            "source": source,
                            "data": data
                        }
                        for source, data in item_data["sources"].items()
                        if data  # Only include non-empty data
                    ]
                }
                for item_data in flat_data.values()
                if any(data for data in item_data["sources"].values())  # Only include items with non-empty content
            ],
            "metadata": metadata
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load_supporting_data")
async def load_supporting_data(payload: Union[List[Dict[str, Any]], Dict[str, Any]] = Body(...)):
    """
    Load supporting data from various file types (email marketing, social media, retail).

    Expected body format (array):
    [
        {
            "id": "69068ae525a393e0435f00d5",
            "fileName": "Customer_Feedback.xlsx",
            "type": "Retail",
            "uploadedBy": "admin@example.com",
            "status": "Pending",
            "bucketName": "my-uploads-bucket",
            "s3Key": "uploads/customer_feedback.xlsx",
            "createdAt": "2025-11-05T16:00:00.000Z",
            "updatedAt": "2025-11-05T16:00:00.000Z"
        },
        ...
    ]

    Alternative format (object with files key):
    {
        "files": [
            {
                "id": "69068ae525a393e0435f00d5",
                "fileName": "Customer_Feedback.xlsx",
                "type": "Retail",
                ...
            }
        ]
    }

    Legacy format (still supported):
    {
        "delivery_file_path": "/path/to/Advertising_Email_Deliveries_2024.xlsx",
        "engagement_file_path": "/path/to/Advertising_Email_Engagement_2024.xlsx",
        "performance_file_path": "/path/to/Advertising_Email_Performance_2024.xlsx",
        "social_media_file_path": "/path/to/Social_Media_Performance.xlsx",
        "retail_file_path": "/path/to/retail_data.parquet"
    }
    """
    print("Payload received for supporting data load:", payload)
    try:
        # Normalize payload to dictionary format
        if isinstance(payload, list):
            # If payload is an array, wrap it in a dictionary with 'files' key
            payload = {"files": payload}
        # Initialize file paths
        delivery_file = None
        engagement_file = None
        performance_file = None
        social_media_file = None
        retail_file = None

        # Initialize variables
        s3_bucket = None
        user_email = None
        
        # Collect file names for email notification
        processed_files = []
        
        # Track period extracted from files
        extracted_period = None

        # Check if new format with files array is provided
        if "files" in payload and isinstance(payload["files"], list):
            # Process new format with files array
            for file_info in payload["files"]:
                # Support both camelCase (fileName) and lowercase (filename)
                original_file_name = file_info.get("fileName") or file_info.get("filename") or ""
                file_name = original_file_name.lower()
                file_type = file_info.get("type", "").lower()
                s3_key = file_info.get("s3Key", "")
                bucket_name = file_info.get("bucketName", "")
                
                # Collect file names for notification
                if original_file_name:
                    processed_files.append(original_file_name)

                # Set bucket name from first file (assuming all files are in same bucket)
                if not s3_bucket and bucket_name:
                    s3_bucket = bucket_name
                
                # Get user email from the first file that has it
                if not user_email and file_info.get("uploadedBy"):
                    user_email = file_info.get("uploadedBy")
                
                # Get period from the first file that has it
                if not extracted_period and file_info.get("period"):
                    extracted_period = file_info.get("period")

                # Map files based on type first, then filename patterns
                if file_type.lower() == "retail data" or file_type.lower() == "retail":
                    retail_file = s3_key
                elif file_type.lower() == "email delivery":
                    delivery_file = s3_key
                elif file_type.lower() == "email engagement":
                    engagement_file = s3_key
                elif file_type.lower() == "email performance":
                    performance_file = s3_key
                elif file_type.lower() == "social media":
                    social_media_file = s3_key
                # Fallback to filename patterns if type doesn't match
                elif "retail" in file_name.lower():
                    retail_file = s3_key
                elif "deliver" in file_name.lower():
                    delivery_file = s3_key
                elif "engagement" in file_name.lower():
                    engagement_file = s3_key
                elif "performance" in file_name.lower() and "social" not in file_name.lower():
                    performance_file = s3_key
                elif "social" in file_name.lower() or "media" in file_name.lower():
                    social_media_file = s3_key

        else:
            # Fallback to legacy format
            delivery_file = payload.get("delivery_file_path")
            engagement_file = payload.get("engagement_file_path")
            performance_file = payload.get("performance_file_path")
            social_media_file = payload.get("social_media_file_path")
            retail_file = payload.get("retail_file_path")
            # For legacy format, add file names if provided
            for f in [delivery_file, engagement_file, performance_file, social_media_file, retail_file]:
                if f:
                    processed_files.append(f.split("/")[-1] if "/" in f else f)

        # Check if at least one file type is provided
        if not any([delivery_file, engagement_file, performance_file, social_media_file, retail_file]):
            raise HTTPException(status_code=400, detail="At least one file must be provided")

        # Create loader instance with provided file paths, S3 bucket, and user_id
        loader = SupportingDataLoader(delivery_file, engagement_file, performance_file, social_media_file, retail_file, s3_bucket, user_id=user_email)

        # Track success/failure for email notification
        load_success = False
        error_message = None
        
        try:
            # Load the data needed for reports
            loader.load_all_data()
            load_success = True
        except Exception as load_error:
            load_success = False
            error_message = str(load_error)
            logger.error(f"Data load failed: {error_message}")

        # Send email notification if user email is provided
        if user_email:
            email_service = EmailService()
            
            # Build file list HTML
            files_html = ""
            files_text = ""
            if processed_files:
                files_html = "<h3 style='margin-top: 20px; margin-bottom: 10px;'>Files Processed:</h3><ul style='margin: 0; padding-left: 20px;'>"
                for fname in processed_files:
                    files_html += f"<li style='margin: 5px 0;'>{fname}</li>"
                files_html += "</ul>"
                files_text = "\n\nFiles Processed:\n" + "\n".join(f"- {fname}" for fname in processed_files)
            
            if load_success:
                # Success email
                subject = "✅ AI Report Agent: Data Load Completed Successfully"
                body_text = f"Your data load request has been successfully completed. You can now generate reports using the loaded data.{files_text}"
                body_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
                            <h2 style="color: #28a745; margin-top: 0;">✅ Data Load Completed Successfully</h2>
                            <p>Your data load request has been successfully completed.</p>
                            <p>You can now generate reports using the loaded data.</p>
                            {files_html}
                            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                            <p style="font-size: 12px; color: #666;">
                                This is an automated message from AI Report Agent.
                            </p>
                        </div>
                    </body>
                </html>
                """
            else:
                # Failure email
                subject = "❌ AI Report Agent: Data Load Failed"
                body_text = f"Unfortunately, your data load request could not be completed. Please re-upload your files and try again.{files_text}"
                body_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
                            <h2 style="color: #dc3545; margin-top: 0;">❌ Data Load Failed</h2>
                            <p>Unfortunately, your data load request could not be completed.</p>
                            <p><strong>Please re-upload your files and try again.</strong></p>
                            <p>If the problem persists after multiple attempts, please contact support for assistance.</p>
                            {files_html}
                            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                            <p style="font-size: 12px; color: #666;">
                                This is an automated message from AI Report Agent.
                            </p>
                        </div>
                    </body>
                </html>
                """
            
            email_service.send_notification(user_email, subject, body_text, body_html)

        # Trigger automatic report generation after successful data load
        if load_success:
            try:
                # Extract period from payload metadata
                period = None
                # Attempt to extract period from the payload's metadata if available
                if "metadata" in payload and isinstance(payload["metadata"], dict):
                    period = payload["metadata"].get("period")
                
                # Fallback: if period not in metadata, check if it's directly in payload
                if not period and "period" in payload:
                    period = payload.get("period")
                
                # Fallback: use period extracted from file_info objects
                if not period and extracted_period:
                    period = extracted_period
                
                # Only trigger report generation if we have a valid period
                if period:
                    # Trigger report generation
                    report_payload = {
                        "reportType": "All Categories",
                        "period": period
                    }
                    
                    async with httpx.AsyncClient(timeout=500.0) as client:
                        response = await client.post(
                            "http://host.docker.internal:3000/api/reports/generate",
                            json=report_payload
                        )
                        
                        if response.status_code == 200:
                            logger.info(f"Report generation triggered successfully for period {report_payload['period']}")
                        else:
                            logger.warning(f"Report generation request returned status {response.status_code}")
                else:
                    logger.warning("No period found in payload metadata. Skipping automatic report generation.")
                        
            except Exception as report_error:
                # Don't fail the data load if report generation fails
                logger.error(f"Failed to trigger automatic report generation: {report_error}")

        # Return appropriate response
        if load_success:
            return {"message": "Supporting data loaded successfully"}
        else:
            raise HTTPException(status_code=500, detail=error_message)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Send failure email for unexpected errors if we have user email
        if 'user_email' in locals() and user_email:
            try:
                email_service = EmailService()
                subject = "❌ AI Report Agent: Data Load Failed"
                body_text = "Unfortunately, your data load request could not be completed. Please re-upload your files and try again."
                body_html = """
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
                            <h2 style="color: #dc3545; margin-top: 0;">❌ Data Load Failed</h2>
                            <p>Unfortunately, your data load request could not be completed.</p>
                            <p><strong>Please re-upload your files and try again.</strong></p>
                            <p>If the problem persists after multiple attempts, please contact support for assistance.</p>
                            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
                            <p style="font-size: 12px; color: #666;">
                                This is an automated message from AI Report Agent.
                            </p>
                        </div>
                    </body>
                </html>
                """
                email_service.send_notification(user_email, subject, body_text, body_html)
            except Exception as email_error:
                logger.error(f"Failed to send error notification email: {email_error}")
        
        raise HTTPException(status_code=500, detail=str(e))
