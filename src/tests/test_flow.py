import requests

def test_generate_report():
    url = "http://127.0.0.1:8000/generate_report"
    headers = {"Content-Type": "application/json"}
    mock_data = {
        "data": [],  # Array of database records would go here
        "metadata": {
            "reportType": "retail",
            "period": "2024-09",
            "dateRange": {
                "startDate": "2024-09-01",
                "endDate": "2024-09-30"
            },
            "recordCount": 1500
        }
    }
    response = requests.post(url, json=mock_data, headers=headers)
    print("Status:", response.status_code)
    print("Response JSON:")
    print(response.json())

if __name__ == "__main__":
    test_generate_report()
