import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import asyncio

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.report_automation_service import ReportAutomationService

class TestReportAutomationService(unittest.TestCase):
    @patch('src.services.report_automation_service.ParallelReportGenerator')
    @patch('src.services.report_automation_service.MongoConnection')
    def test_generate_and_store_report_success(self, mock_mongo_cls, mock_generator_cls):
        # Setup mocks
        mock_generator = mock_generator_cls.return_value
        mock_generator.generate_reports = AsyncMock(return_value=[{"report": "data"}])

        mock_mongo = mock_mongo_cls.return_value
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_mongo.get_db.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value.inserted_id = "test_id"

        # Initialize service
        service = ReportAutomationService()

        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(service.generate_and_store_report({"metadata": {}}))
        loop.close()

        # Verify
        self.assertEqual(result, "test_id")
        mock_generator.generate_reports.assert_called_once()
        mock_collection.insert_one.assert_called_once()

    @patch('src.services.report_automation_service.ParallelReportGenerator')
    @patch('src.services.report_automation_service.MongoConnection')
    def test_generate_and_store_report_failure(self, mock_mongo_cls, mock_generator_cls):
        # Setup mocks to return empty list (failure)
        mock_generator = mock_generator_cls.return_value
        mock_generator.generate_reports = AsyncMock(return_value=[])

        # Initialize service
        service = ReportAutomationService()

        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(service.generate_and_store_report({"metadata": {}}))
        loop.close()

        # Verify
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
