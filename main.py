from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Body
from src.services.retrievers import get_mock_data
from src.services.parallel_report_generator import ParallelReportGenerator
from src.models.report_schema import get_report_schema
from src.file_operations.load_email_marketing_data import SupportingDataLoader
import asyncio
import re
import unicodedata

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

        # Load report structure based on report type
        structure = get_report_schema(report_type).dict()

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
        if report_type == "retail_data":
            print(f"Processing retail data report (type: {report_type})")
            # Add retail-specific processing logic here

        elif report_type == "all_categories":
            print(f"Processing all categories report (type: {report_type})")
            # Add comprehensive data processing logic here

        elif report_type == "email_performance":
            print(f"Processing email performance report (type: {report_type})")
            # Add email-specific processing logic here

        elif report_type == "social_media_data":
            print(f"Processing social media data report (type: {report_type})")
            # Add social media-specific processing logic here

        else:
            print(f"Processing report with unknown type: '{report_type}' - using default logic")
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
def load_supporting_data(payload: Dict[str, Any] = Body(...)):
    """
    Load supporting data from various file types (email marketing, social media, retail).

    Expected body format:
    {
        "files": [
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
    }

    Alternative legacy format (still supported):
    {
        "delivery_file_path": "/path/to/Advertising_Email_Deliveries_2024.xlsx",
        "engagement_file_path": "/path/to/Advertising_Email_Engagement_2024.xlsx",
        "performance_file_path": "/path/to/Advertising_Email_Performance_2024.xlsx",
        "social_media_file_path": "/path/to/Social_Media_Performance.xlsx",
        "retail_file_path": "/path/to/retail_data.parquet"
    }
    """
    try:
        # Initialize file paths
        delivery_file = None
        engagement_file = None
        performance_file = None
        social_media_file = None
        retail_file = None

        # Initialize variables
        s3_bucket = None

        # Check if new format with files array is provided
        if "files" in payload and isinstance(payload["files"], list):
            # Process new format with files array
            for file_info in payload["files"]:
                file_name = file_info.get("fileName", "").lower()
                file_type = file_info.get("type", "").lower()
                s3_key = file_info.get("s3Key", "")
                bucket_name = file_info.get("bucketName", "")

                # Set bucket name from first file (assuming all files are in same bucket)
                if not s3_bucket and bucket_name:
                    s3_bucket = bucket_name

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

        # Check if at least one file type is provided
        if not any([delivery_file, engagement_file, performance_file, social_media_file, retail_file]):
            raise HTTPException(status_code=400, detail="At least one file must be provided")

        # Create loader instance with provided file paths and S3 bucket
        loader = SupportingDataLoader(delivery_file, engagement_file, performance_file, social_media_file, retail_file, s3_bucket)

        # Load the data needed for reports
        loader.load_all_data()

        return {"message": "Supporting data loaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
