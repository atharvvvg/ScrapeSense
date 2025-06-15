# /ScrapeSense/config/settings.py
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "ScrapeSense_db_mvp" # Specific for MVP

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-pro") 