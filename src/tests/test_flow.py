import requests

def test_generate_report():
    url = "http://127.0.0.1:8000/generate_report"
    response = requests.post(url)
    print("Status:", response.status_code)
    print("Response JSON:")
    print(response.json())

if __name__ == "__main__":
    test_generate_report()
