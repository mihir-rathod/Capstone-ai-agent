# 🧠 Capstone-ai-agent - MCCS Marketing Analytics Mock API

A FastAPI-based **mock backend** that returns a realistic, multi-page JSON response simulating the **MCCS Marketing Analytics Assessment Report**.  

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Request/Response Format](#requestresponse-format)
- [Resources](#resources)

---

## ✨ Features

- Returns **multi-page structured JSON** report output  
- Follows **real MCCS report schema** for September 2024  
- Includes **Purpose, Executive Summary, Findings, CSAT, and Social Media Insights**  
- FastAPI with automatic Swagger UI  
- **Dockerized** for consistent deployment  
- Schema endpoint (`/api/v1/report-structure`) for frontend validation  

---

## 📁 Project Structure

```
CAPSTONE-AI-AGENT/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── routers/
│   │   └── mock.py                # Mock API endpoints (multi-page MCCS report)
│   ├── ai/                        # Gemini AI integration
│   └── database/                  # Database connection module
├── Dockerfile                     # Docker container configuration
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

---

## 🔧 Prerequisites

- **Docker**
- **Git**
- (Optional) **Python 3.9+** for local runs

---

## 🚀 Installation

### 🐳 Run via Docker

```bash
# Clone repository
git clone <repository-url>
cd CAPSTONE-AI-AGENT

# Build Docker image
docker build -t capstone-api .

# Run container
docker run -p 8000:8000 capstone-api
```

API available at: **http://localhost:8000**

---

## 📍 API Endpoints

**Base URL:** `http://localhost:8000`

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/` | API root status |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (interactive API docs) |
| `POST` | `/api/v1/generate-report` | Generate full mock report |
| `GET` | `/api/v1/report-structure` | View schema structure by page |

---

## 🧪 Testing

### 🧭 Swagger UI (Recommended)

1. Start API:  
   ```bash
   docker run -p 8000:8000 capstone-api
   ```
2. Open browser: [http://localhost:8000/docs](http://localhost:8000/docs)
3. Select `POST /api/v1/generate-report`
4. Click **Try it out**
5. Example body:
   ```json
   {
     "user_input": "Generate marketing analytics report for September 2024",
     "report_type": "marketing_analytics",
     "month": "September",
     "year": "2024"
   }
   ```
6. Click **Execute**

---

### 🧩 Using cURL

**Linux/Mac**
```bash
curl -X POST "http://localhost:8000/api/v1/generate-report"   -H "Content-Type: application/json"   -d '{
    "user_input": "Generate marketing analytics report for September 2024",
    "report_type": "marketing_analytics",
    "month": "September",
    "year": "2024"
  }'
```

**Windows PowerShell**
```powershell
$body = @{
    user_input = "Generate marketing analytics report for September 2024"
    report_type = "marketing_analytics"
    month = "September"
    year = "2024"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/generate-report" -Method Post -Body $body -ContentType "application/json"
```

**Python**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate-report",
    json={
        "user_input": "Generate marketing analytics report for September 2024",
        "report_type": "marketing_analytics",
        "month": "September",
        "year": "2024"
    }
)
print(response.json())
```

---

## 📝 Request/Response Format

### **Sample Request**
```json
{
  "user_input": "Generate marketing analytics report for September 2024",
  "report_type": "marketing_analytics",
  "month": "September",
  "year": "2024"
}
```

### **Sample Response (simplified)**
```json
{
  "report_id": "a2c8eab6-8fa2-4d9b-b312-85c9f7b7af2b",
  "timestamp": "2024-11-27T15:05:44.513Z",
  "status": "success",
  "report_metadata": {
    "report_type": "marketing_analytics",
    "month": "September",
    "year": "2024",
    "total_pages": 3
  },
  "page_1": {
    "report_title": "September 2024 MCCS Marketing Analytics Assessment",
    "purpose_statement": "To support leaders and subject matter experts...",
    "exec_summary_bullets": [
      "Labor Day Promotion increased sales by 6.8% over LY",
      "September Email Open Rate (OPR) reached 38.08%",
      "Promotions with time-sensitivity boosted engagement"
    ],
    "findings_digital_header": "Findings – Review of digital performance..."
  },
  "page_2": {
    "email_highlight_header": "September MCX Email Highlight",
    "email_campaigns_table": [ ... ],
    "social_media_header": "September MCX Social Media Highlights"
  },
  "page_3": {
    "customer_satisfaction_header": "September MCX Customer Satisfaction Highlights",
    "main_exchange_comments": [ ... ],
    "google_reviews_details": [ ... ]
  }
}
```

---

## 🧠 Mock Report Schema Overview

| Page | Content Highlights |
|------|---------------------|
| **Page 1** | Cover Page, Purpose, Executive Summary, Digital Performance, CSAT Findings |
| **Page 2** | Email Campaigns, Social Media Highlights, Engagement Metrics |
| **Page 3** | Customer Satisfaction Comments, Google Reviews, Satisfaction Tables |

Use the endpoint `/api/v1/report-structure` for schema details.

---

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Docker Docs](https://docs.docker.com/)
- [Uvicorn Docs](https://www.uvicorn.org/)

---

> **Note:** This API serves as a *mock* backend for development and integration testing.