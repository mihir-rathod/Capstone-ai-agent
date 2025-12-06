from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class MongoConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance

    def connect(self):
        if self.client is None:
            try:
                self.client = MongoClient(settings.MONGO_URI)
                # Verify connection
                self.client.admin.command('ping')
                self.db = self.client[settings.MONGO_DB_NAME]
                logger.info("Successfully connected to MongoDB")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise

    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed")
