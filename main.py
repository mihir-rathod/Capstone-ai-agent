from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from src.services.retrievers import get_mock_data
from src.services.parallel_report_generator import ParallelReportGenerator
from src.models.report_schema import marketing_report_schema as ReportStructure
import asyncio

app = FastAPI(title="Report Generation API")

@app.get("/")
def root():
    return {"message": "✅ Report Generation API is running"}

@app.post("/generate_report")
async def generate_report_endpoint():
    try:
        # Load predefined report structure
        structure = ReportStructure.dict()

        # Get context data (mock for now)
        context = get_mock_data()

        # Initialize parallel report generator
        generator = ParallelReportGenerator()
        
        # Generate reports using multiple LLMs
        reports = await generator.generate_reports(structure, context)

        # Build status for each LLM
        status_map = {r["source"]: ("success" if r["validation"]["is_valid"] else "error") for r in reports}

        # Aggregate tags across both reports as before
        combined_content = []
        processed_tags = set()
        for report in reports:
            for page in report["report"]["pages"]:
                for tag in page["tags"]:
                    tag_id = tag["id"]
                    if tag_id in processed_tags:
                        continue
                    combined_tag = {
                        "id": tag_id,
                        "title": tag["title"],
                        "content": []
                    }
                    for r in reports:
                        src = r["source"]
                        for p in r["report"]["pages"]:
                            for t in p["tags"]:
                                if t["id"] == tag_id and t.get("content"):
                                    combined_tag["content"].append({
                                        "source": src,
                                        "data": str(t["content"])
                                    })
                    combined_content.append(combined_tag)
                    processed_tags.add(tag_id)

        response = {
            "content": combined_content,
            "metadata": {
                "Gemini_status": status_map.get("Gemini", "error"),
                "Ollama_status": status_map.get("Ollama", "error"),
                "parallel_generation": generator.parallel_generation,
                "total_reports": len(reports),
                "valid_reports": sum(1 for r in reports if r["validation"]["is_valid"]),
                "regeneration_attempts": sum(1 for r in reports if r.get("regeneration_attempt", 0) > 0)
            }
        }
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
