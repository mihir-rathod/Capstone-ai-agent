import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock ollama module before importing main
sys.modules["ollama"] = MagicMock()

from main import app

client = TestClient(app)

@pytest.fixture
def mock_dependencies():
    with patch("main.SupportingDataLoader") as mock_loader_cls, \
         patch("main.EmailService") as mock_email_cls, \
         patch("httpx.AsyncClient") as mock_httpx_client:
        
        # Setup mock loader
        mock_loader = mock_loader_cls.return_value
        mock_loader.load_all_data.return_value = None
        
        # Setup mock email service
        mock_email = mock_email_cls.return_value
        mock_email.send_notification.return_value = None
        
        yield {
            "loader_cls": mock_loader_cls,
            "email_cls": mock_email_cls,
            "httpx_client": mock_httpx_client
        }

def test_load_supporting_data_lowercase_filename(mock_dependencies):
    payload = [
        {
            "filename": "RetailData(Jan-24).parquet",
            "type": "application/octet-stream",
            "uploadedBy": "Capstone",
            "bucketName": "mccs-capstone-s3",
            "s3Key": "uploads/1765042788274-g3bnm0-retaildata_jan-24_.parquet"
        }
    ]
    
    response = client.post("/load_supporting_data", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"message": "Supporting data loaded successfully"}
    
    # Verify that the loader was initialized with the correct retail file
    # The logic in main.py maps "RetailData(Jan-24).parquet" to retail_file based on "Retail" in filename
    # or type "application/octet-stream" (which doesn't match specific types)
    # Let's check how main.py logic works:
    # file_name = "retaildata(jan-24).parquet"
    # "retail" in file_name is True.
    # So it should be assigned to retail_file.
    
    mock_dependencies["loader_cls"].assert_called_once()
    call_args = mock_dependencies["loader_cls"].call_args
    # Args: delivery_file, engagement_file, performance_file, social_media_file, retail_file, s3_bucket
    # We expect retail_file (5th arg) to be the s3Key
    
    args = call_args[0]
    assert args[4] == "uploads/1765042788274-g3bnm0-retaildata_jan-24_.parquet"
    assert args[5] == "mccs-capstone-s3"

if __name__ == "__main__":
    # Manually run the test function if executed as a script
    # This is just a helper to run it without pytest installed if needed, 
    # but we'll try to run with pytest first.
    try:
        # Create mocks manually
        with patch("main.SupportingDataLoader") as mock_loader_cls, \
             patch("main.EmailService") as mock_email_cls, \
             patch("httpx.AsyncClient") as mock_httpx_client:
            
            mock_loader = mock_loader_cls.return_value
            mock_loader.load_all_data.return_value = None
            
            mock_deps = {
                "loader_cls": mock_loader_cls,
                "email_cls": mock_email_cls,
                "httpx_client": mock_httpx_client
            }
            
            test_load_supporting_data_lowercase_filename(mock_deps)
            print("Test passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
