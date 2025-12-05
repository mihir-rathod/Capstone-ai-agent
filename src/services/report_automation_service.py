from src.services.parallel_report_generator import ParallelReportGenerator
from src.models.report_schema import get_report_schema
from src.database.mongo_connection import MongoConnection
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class ReportAutomationService:
    def __init__(self):
        self.generator = ParallelReportGenerator()
        self.mongo = MongoConnection()

    async def generate_and_store_report(self, context_data: dict):
        """
        Generates an 'all-categories' report and stores it in MongoDB.
        """
        try:
            # Determine requested report type from metadata (accept many variants)
            from src.services.report_types import normalize_report_type

            requested = context_data.get('metadata', {}).get('reportType')
            report_type = normalize_report_type(requested)
            logger.info(f"Starting automated report generation for type: {report_type}")

            # Get schema
            structure = get_report_schema(report_type).dict()

            # Generate report
            reports = await self.generator.generate_reports(structure, context_data)

            if not reports:
                logger.error("Report generation failed: No reports generated")
                return False

            # Store in MongoDB
            db = self.mongo.get_db()
            collection = db["reports"]

            # Prepare document
            document = {
                "report_type": report_type,
                "created_at": datetime.utcnow(),
                "context_metadata": context_data.get("metadata", {}),
                "reports": reports,
                "status": "completed"
            }

            result = collection.insert_one(document)
            logger.info(f"Report stored in MongoDB with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Error in automated report generation: {str(e)}")
            return False
