# /ScrapeSense/scripts/setup_initial_config.py
from database.mongo_client import get_db_connection
from database.schemas import ScrapingTarget, FieldToExtract

# Note: The Engineer LLM must replace "/full/path/to/" with the correct absolute path
MVP_TARGET_ID = "mvp_test_page"
MVP_TARGET_URL = "file:///C:/Users/athar/Desktop/projects/ScrapeSense/data/test_page.html"

def setup_config():
    db = get_db_connection()
    targets_collection = db["targets"]

    mvp_target_config_data = {
        "_id": MVP_TARGET_ID, # Pydantic uses target_id, mongo uses _id
        "url": MVP_TARGET_URL,
        "fields": [
            {
                "name": "product_title",
                "description": "The main H1 title of the product",
                "current_selector": "h1" # Initial correct selector
            }
        ],
        "is_broken": False
    }
    
    # Validate with Pydantic before inserting/replacing
    mvp_target_config = ScrapingTarget(**mvp_target_config_data)

    # Use model_dump(by_alias=True) to ensure _id is used for MongoDB
    targets_collection.replace_one(
        {"_id": mvp_target_config.target_id}, 
        mvp_target_config.model_dump(by_alias=True), 
        upsert=True
    )
    print(f"Configuration for '{MVP_TARGET_ID}' upserted into MongoDB.")

if __name__ == "__main__":
    setup_config() 