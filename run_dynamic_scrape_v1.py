# /ScrapeSense/run_dynamic_scrape_v1.py
import asyncio
from database.mongo_client import get_db_connection
from database.schemas import ScrapingTarget
from scraper_core.browser_manager import get_page_dom
from scraper_core.extraction_engine import extract_data_with_selector

MVP_TARGET_ID = "mvp_test_page"

async def main():
    db = get_db_connection()
    targets_collection = db["targets"]
    
    config_dict = targets_collection.find_one({"_id": MVP_TARGET_ID})

    if not config_dict:
        print(f"Configuration for target_id '{MVP_TARGET_ID}' not found in MongoDB.")
        return

    try:
        target_config = ScrapingTarget(**config_dict)
    except Exception as e:
        print(f"Error parsing target configuration: {e}")
        return

    if not target_config.fields:
        print("No fields to extract in target configuration.")
        return
    
    field_to_extract = target_config.fields[0] # MVP: only first field
    url_to_scrape = target_config.url
    selector = field_to_extract.current_selector

    if not selector:
        print(f"No selector defined for field '{field_to_extract.name}'.")
        return

    print(f"Attempting to scrape: {url_to_scrape} for field '{field_to_extract.name}' using selector '{selector}'")
    dom = await get_page_dom(url_to_scrape)

    if dom:
        extracted_data = extract_data_with_selector(dom, selector)
        if extracted_data:
            print(f"Extracted data: {extracted_data}")
        else:
            print(f"Data not found using selector '{selector}'.")
    else:
        print("Failed to fetch DOM.")

if __name__ == "__main__":
    asyncio.run(main()) 