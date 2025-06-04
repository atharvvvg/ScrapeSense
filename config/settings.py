# /ScrapeSense/config/settings.py
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "ScrapeSense_db_mvp" # Specific for MVP 