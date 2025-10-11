from fastapi import FastAPI, HTTPException
from src.services.retrievers import get_mock_data
from src.services.llm_generator import generate_report
from src.services.llm_validator import validate_report
from src.models.report_schema import marketing_report_schema as ReportStructure

app = FastAPI(title="Report Generation API")

@app.get("/")
def root():
    return {"message": "✅ Report Generation API is running"}

@app.post("/generate_report")
def generate_report_endpoint():
    try:
        # Load predefined report structure (generic dict)
        structure = ReportStructure.dict()

        # Get context data (mock for now)
        context = get_mock_data()

        # Generate report via Gemini
        report = generate_report(structure, context)

        # Validate report
        validation = validate_report(structure, report)

        if validation.is_valid:
            return {"status": "success", "report": report}
        else:
            return {"status": "error", "message": validation.message, "raw_report": report}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
