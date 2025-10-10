# Capstone-ai-agent - Mock API

A FastAPI-based mock API that returns structured JSON responses simulating marketing analytics reports.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)

## ✨ Features

- Mock report generation with structured data
- CORS enabled for cross-origin requests
- Interactive API documentation (Swagger UI)
- Type validation with Pydantic
- Dockerized deployment

## 📁 Project Structure

```
CAPSTONE-AI-AGENT/
├── src/
│   ├── main.py                    # FastAPI application entry point
│   ├── routers/
│   │   └── mock.py                # Mock API endpoints for report generation
│   ├── ai/                        # AI/LLM integration 
│   └── database/                  # Database connection 
├── Dockerfile                     # Docker container configuration
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

## 🔧 Prerequisites

- Docker
- Git

## 🚀 Installation

```bash
# Clone repository
git clone <repository-url>
cd CAPSTONE-AI-AGENT

# Build Docker image
docker build -t capstone-api .

# Run container
docker run -p 8000:8000 capstone-api
```

API available at: `http://localhost:8000`

## 📍 API Endpoints

**Base URL:** `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API docs |
| POST | `/api/v1/generate-report` | Generate mock report |
| GET | `/api/v1/report-example` | Example request/response |

## 🧪 Testing

### Interactive Docs (Recommended)

1. Start API: `docker run -p 8000:8000 capstone-api`
2. Open: `http://localhost:8000/docs`
3. Click `POST /api/v1/generate-report`
4. Click **"Try it out"**
5. Use example request body:
```json
{
  "user_input": "Generate marketing analytics report",
  "report_type": "marketing_analytics",
  "month": "September",
  "year": "2024"
}
```
6. Click **"Execute"**

### cURL (Windows PowerShell)

```powershell
$body = @{
    user_input = "Generate marketing analytics report"
    report_type = "marketing_analytics"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/generate-report" -Method Post -Body $body -ContentType "application/json"
```

### cURL (Linux/Mac)

```bash
curl -X POST "http://localhost:8000/api/v1/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Generate marketing analytics report",
    "report_type": "marketing_analytics"
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate-report",
    json={
        "user_input": "Generate marketing analytics report",
        "report_type": "marketing_analytics"
    }
)
print(response.json())
```

## 📝 Request/Response Format

**Minimal Request:**
```json
{
  "user_input": "Generate report"
}
```

**Full Request:**
```json
{
  "user_input": "Generate marketing analytics report for September 2024",
  "report_type": "marketing_analytics",
  "month": "September",
  "year": "2024"
}
```

**Response Structure:**
```json
{
  "report_id": "uuid",
  "timestamp": "2024-10-10T12:00:00",
  "status": "success",
  "report_metadata": { ... },
  "summary": "Executive summary...",
  "email_campaigns": { ... },
  "customer_satisfaction": { ... },
  "customer_feedback": { ... },
  "key_insights": [ ... ],
  "recommendations": [ ... ]
}
```

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Docker Docs](https://docs.docker.com/)

---

**Note:** This is a mock API with dummy data for development purposes.