from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Body
from src.services.retrievers import get_mock_data
from src.services.parallel_report_generator import ParallelReportGenerator
from src.models.report_schema import marketing_report_schema as ReportStructure
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
        # Load predefined report structure
        structure = ReportStructure.dict()

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

        # Get metadata from context
        metadata = {}
        if isinstance(context_data, dict):
            # If metadata is directly in the context
            if "metadata" in context_data:
                metadata = context_data["metadata"]
            # For backward compatibility - convert old filterValue structure
            elif "filterValue" in context_data:
                filter_data = context_data["filterValue"]
                metadata = {
                    "reportType": str(filter_data.get("reportType", "")),
                    "period": str(filter_data.get("period", "")),
                    "dateRange": {
                        "startDate": "",
                        "endDate": ""
                    },
                    "recordCount": 0
                }

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
def load_supporting_data(file_paths: Dict[str, str] = Body(...)):
    """
    Load supporting data from various file types (email marketing, social media, retail).

    Expected body:
    {
        "delivery_file_path": "/path/to/Advertising_Email_Deliveries_2024.xlsx",  # optional
        "engagement_file_path": "/path/to/Advertising_Email_Engagement_2024.xlsx",  # optional
        "performance_file_path": "/path/to/Advertising_Email_Performance_2024.xlsx",  # optional
        "social_media_file_path": "/path/to/Social_Media_Performance.xlsx",  # optional
        "retail_file_path": "/path/to/retail_data.parquet"  # optional
    }
    """
    try:
        delivery_file = file_paths.get("delivery_file_path")
        engagement_file = file_paths.get("engagement_file_path")
        performance_file = file_paths.get("performance_file_path")
        social_media_file = file_paths.get("social_media_file_path")
        retail_file = file_paths.get("retail_file_path")

        # Check if at least one file type is provided
        if not any([delivery_file, engagement_file, performance_file, social_media_file, retail_file]):
            raise HTTPException(status_code=400, detail="At least one file path must be provided")

        # Create loader instance with provided file paths
        loader = SupportingDataLoader(delivery_file, engagement_file, performance_file, social_media_file, retail_file)

        # Load the data needed for reports
        loader.load_all_data()

        return {"message": "Supporting data loaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
