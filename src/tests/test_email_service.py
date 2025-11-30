import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.email_service import EmailService

class TestEmailService(unittest.TestCase):
    @patch('smtplib.SMTP')
    def test_send_notification_success(self, mock_smtp):
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Initialize service
        service = EmailService()
        
        # Test sending
        result = service.send_notification(
            recipient_email="test@example.com",
            subject="Test Subject",
            body_text="Test Body"
        )

        # Verify
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_notification_no_recipient(self, mock_smtp):
        service = EmailService()
        result = service.send_notification(None, "Subject", "Body")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
