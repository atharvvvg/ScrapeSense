# /ScrapeSense/database/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
# from datetime import datetime # Not used in MVP schema yet

class FieldToExtract(BaseModel):
    name: str  # e.g., "product_title"
    description: str
    current_selector: Optional[str] = None

class ScrapingTarget(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    target_id: str = Field(..., alias="_id") # Use target_id as primary key _id
    url: str
    fields: List[FieldToExtract]
    is_broken: bool = False 