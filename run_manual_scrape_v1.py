# /ScrapeSense/run_manual_scrape_v1.py
import asyncio
from scraper_core.browser_manager import get_page_dom
from scraper_core.extraction_engine import extract_data_with_selector

# Note: The Engineer LLM must replace "/full/path/to/" with the correct absolute path
TARGET_URL = "file:///C:/Users/athar/Desktop/projects/ScrapeSense/data/test_page.html"
TARGET_FIELD_DESCRIPTION_MVP = "The main H1 title of the product"
INITIAL_SELECTOR_MVP = "h1"

async def main():
    print(f"Attempting to scrape: {TARGET_URL}")
    dom = await get_page_dom(TARGET_URL)
    if dom:
        print("DOM fetched successfully.")
        extracted_data = extract_data_with_selector(dom, INITIAL_SELECTOR_MVP)
        if extracted_data:
            print(f"Extracted data for '{TARGET_FIELD_DESCRIPTION_MVP}': {extracted_data}")
        else:
            print(f"Data not found for selector '{INITIAL_SELECTOR_MVP}'.")
    else:
        print("Failed to fetch DOM.")

if __name__ == "__main__":
    asyncio.run(main()) 