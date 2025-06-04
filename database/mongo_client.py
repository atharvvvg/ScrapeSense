# /ScrapeSense/database/mongo_client.py
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from config import settings # Adjusted import

_client: Optional[MongoClient] = None

def get_db_connection() -> Database:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client[settings.DATABASE_NAME] 