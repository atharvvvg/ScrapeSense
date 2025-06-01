# MVP Build Plan: Self-Learning Web Scraper

**MVP Goal:**
Scrape a *single, predefined data point* (e.g., "product title") from a *single, predefined, simple static webpage*. If the scraper fails (simulated by an incorrect selector in the config), manually trigger a process where the LLM suggests a new selector based on the current DOM and the description of the data point. Manually update the configuration with the new selector and verify it works.

**Pre-requisites for the Engineering LLM:**
*   It has access to a Python environment.
*   It can install packages (`pip install ...`).
*   It can execute Python scripts.
*   It has access to a running MongoDB instance.
*   It has a Google Gemini API key available (e.g., as an environment variable).

---

## Phase 1: Basic Scraping Setup & Manual Extraction

### 1. Task 1: Project Skeleton and Virtual Environment
*   **Concern:** Initialize project structure according to `architecture.md` and manage dependencies.
*   **Start:** No project directory.
*   **Action:**
    *   Create the main project folder: `/self_learning_scraper`.
    *   Inside, create a Python virtual environment (e.g., `python -m venv .venv` and ensure it's activated for subsequent tasks).
    *   Create an empty `requirements.txt` at the root.
    *   Create the following folders, each with an empty `__init__.py` file:
        *   `/self_learning_scraper/scraper_core/`
        *   `/self_learning_scraper/llm_adapter/`
        *   `/self_learning_scraper/relearning_manager/` (empty for MVP logic)
        *   `/self_learning_scraper/rl_agent/` (empty for MVP)
        *   `/self_learning_scraper/database/`
        *   `/self_learning_scraper/orchestration/` (empty for MVP)
        *   `/self_learning_scraper/api/` (empty for MVP)
        *   `/self_learning_scraper/config/`
        *   `/self_learning_scraper/utils/`
        *   `/self_learning_scraper/logs/` (empty)
        *   `/self_learning_scraper/data/` (empty)
    *   Create an empty `README.md` at the root.
*   **End:** Project folder structure as per `architecture.md` exists with `__init__.py` files and an active venv. `requirements.txt` is empty.
*   **Test:** Venv can be activated. Listing the directory shows the specified structure.

### 2. Task 2: Install Playwright and Basic Browser Interaction (`browser_manager.py`)
*   **Concern:** Setup web browser automation and a utility to fetch DOM.
*   **Start:** `requirements.txt` is empty. `scraper_core/browser_manager.py` does not exist.
*   **Action:**
    *   Add `playwright` to `/self_learning_scraper/requirements.txt`.
    *   Instruct to run `pip install -r requirements.txt`.
    *   Instruct to run `playwright install` (to install browser drivers).
    *   Create `/self_learning_scraper/scraper_core/browser_manager.py`.
    *   In `browser_manager.py`, define a function `async def get_page_dom(url: str) -> str`:
        ```python
        # /self_learning_scraper/scraper_core/browser_manager.py
        from playwright.async_api import async_playwright

        async def get_page_dom(url: str) -> str:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                content = await page.content()
                await browser.close()
                return content
        ```
*   **End:** `get_page_dom` function exists in `scraper_core/browser_manager.py` and can fetch HTML.
*   **Test:** Create a temporary script (e.g., `test_browser.py`) that imports and calls `await get_page_dom("http://example.com")` and prints the result. It should print example.com's HTML. (Remember to use `asyncio.run()` to execute the async function).
    ```python
    # test_browser.py (temporary test script)
    # import asyncio
    # from self_learning_scraper.scraper_core.browser_manager import get_page_dom

    # async def main():
    #     html_content = await get_page_dom("http://example.com")
    #     print(html_content)

    # if __name__ == "__main__":
    #     asyncio.run(main())
    ```

### 3. Task 3: Define Target URL and Data Point (Hardcoded for Initial Test Script)
*   **Concern:** Specifying what to scrape for the initial manual test.
*   **Start:** No specific target defined for testing.
*   **Action:**
    *   Create a local static HTML file named `test_page.html` in the `/self_learning_scraper/data/` directory:
        ```html
        <!-- /self_learning_scraper/data/test_page.html -->
        <!DOCTYPE html><html><head><title>Test Page</title></head>
        <body><h1>My MVP Product Title</h1><p>Some description.</p>
        <span class="price">$29.99</span></body></html>
        ```
    *   Create a script named `/self_learning_scraper/run_manual_scrape_v1.py`.
    *   In `run_manual_scrape_v1.py`, define:
        ```python
        # /self_learning_scraper/run_manual_scrape_v1.py
        # Note: The Engineer LLM must replace "/full/path/to/" with the correct absolute path
        TARGET_URL = "file:///full/path/to/self_learning_scraper/data/test_page.html"
        TARGET_FIELD_DESCRIPTION_MVP = "The main H1 title of the product"
        INITIAL_SELECTOR_MVP = "h1"
        ```
*   **End:** `run_manual_scrape_v1.py` has these constants, and `data/test_page.html` exists.
*   **Test:** N/A (constants defined). Ensure `test_page.html` is accessible by opening it in a browser using the `file:///` path.

### 4. Task 4: Basic Extraction Logic (`extraction_engine.py`)
*   **Concern:** Extracting data from DOM using a selector.
*   **Start:** `scraper_core/extraction_engine.py` does not exist. `parsel` not installed.
*   **Action:**
    *   Add `parsel` to `/self_learning_scraper/requirements.txt` and instruct to run `pip install -r requirements.txt`.
    *   Create `/self_learning_scraper/scraper_core/extraction_engine.py`.
    *   In `extraction_engine.py`, define a function `extract_data_with_selector(html_dom: str, selector: str) -> Optional[str]`:
        ```python
        # /self_learning_scraper/scraper_core/extraction_engine.py
        from typing import Optional
        import parsel

        def extract_data_with_selector(html_dom: str, selector: str) -> Optional[str]:
            if not html_dom:
                return None
            sel = parsel.Selector(text=html_dom)
            # Using ::text to get all descendant text nodes, then join and strip.
            # .get() returns the first match or None.
            extracted_text_list = sel.css(selector + " ::text").getall()
            if extracted_text_list:
                full_text = "".join(extracted_text_list).strip()
                return full_text if full_text else None
            return None
        ```
*   **End:** `extract_data_with_selector` function exists in `scraper_core/extraction_engine.py`.
*   **Test:** In a temporary script or Python console, import and call `extract_data_with_selector("<body><h1>Test Title</h1></body>", "h1")`. Should return "Test Title". Call with `extract_data_with_selector("<body><p>Another</p></body>", "h1")`; should return `None`.

### 5. Task 5: Simple Scraper Script (`run_manual_scrape_v1.py`)
*   **Concern:** Combining DOM fetching and extraction for the hardcoded target.
*   **Start:** `run_manual_scrape_v1.py` has constants.
*   **Action:**
    *   Complete `/self_learning_scraper/run_manual_scrape_v1.py`:
        ```python
        # /self_learning_scraper/run_manual_scrape_v1.py
        import asyncio
        from self_learning_scraper.scraper_core.browser_manager import get_page_dom
        from self_learning_scraper.scraper_core.extraction_engine import extract_data_with_selector

        # Note: The Engineer LLM must replace "/full/path/to/" with the correct absolute path
        TARGET_URL = "file:///full/path/to/self_learning_scraper/data/test_page.html"
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
        ```
*   **End:** `run_manual_scrape_v1.py` can be run to scrape the target.
*   **Test:** Run `python self_learning_scraper/run_manual_scrape_v1.py`. It should print "Extracted data for 'The main H1 title of the product': My MVP Product Title".

---
## Phase 2: MongoDB for Configuration

### 6. Task 6: MongoDB Settings and Client (`config/settings.py`, `database/mongo_client.py`)
*   **Concern:** Database connection setup.
*   **Start:** No MongoDB interaction files. `pymongo` not installed.
*   **Action:**
    *   Add `pymongo` (or `pymongo[srv]` if using Atlas) to `/self_learning_scraper/requirements.txt` and instruct to run `pip install -r requirements.txt`.
    *   Create `/self_learning_scraper/config/settings.py`. Add:
        ```python
        # /self_learning_scraper/config/settings.py
        import os

        MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        DATABASE_NAME = "self_learning_scraper_db_mvp" # Specific for MVP
        ```
    *   Create `/self_learning_scraper/database/mongo_client.py`.
    *   In `mongo_client.py`, import `MongoClient` from `pymongo` and `MONGO_URI`, `DATABASE_NAME` from `config.settings`.
        ```python
        # /self_learning_scraper/database/mongo_client.py
        from pymongo import MongoClient
        from pymongo.database import Database
        from self_learning_scraper.config import settings # Adjusted import

        _client: Optional[MongoClient] = None

        def get_db_connection() -> Database:
            global _client
            if _client is None:
                _client = MongoClient(settings.MONGO_URI)
            return _client[settings.DATABASE_NAME]
        ```
*   **End:** `get_db_connection` function exists. `settings.py` has DB config.
*   **Test:** In a temporary script, import and call `get_db_connection()`. It should connect without errors. Manually check MongoDB for the database creation if it's the first connection.

### 7. Task 7: Pydantic Schemas for Configuration (`database/schemas.py`)
*   **Concern:** Defining the structure for storing scraping target configuration, as per `architecture.md`.
*   **Start:** `database/schemas.py` does not exist. `pydantic` not installed.
*   **Action:**
    *   Add `pydantic` to `/self_learning_scraper/requirements.txt` and instruct to run `pip install -r requirements.txt`.
    *   Create `/self_learning_scraper/database/schemas.py`.
    *   Define Pydantic models:
        ```python
        # /self_learning_scraper/database/schemas.py
        from typing import List, Optional
        from pydantic import BaseModel, Field
        # from datetime import datetime # Not used in MVP schema yet

        class FieldToExtract(BaseModel):
            name: str  # e.g., "product_title"
            description: str
            current_selector: Optional[str] = None

        class ScrapingTarget(BaseModel):
            target_id: str = Field(..., alias="_id") # Use target_id as primary key _id
            url: str
            fields: List[FieldToExtract]
            is_broken: bool = False

            class Config:
                allow_population_by_field_name = True
                # For MongoDB _id field if it's an ObjectId, but we use string here
                # arbitrary_types_allowed = True
                # json_encoders = {ObjectId: str}
        ```
*   **End:** Pydantic models `FieldToExtract` and `ScrapingTarget` exist in `database/schemas.py`.
*   **Test:** In a Python console, import the models and try creating an instance: `target = ScrapingTarget(target_id="test01", url="http://example.com", fields=[FieldToExtract(name="title", description="main title", current_selector="h1")])`. It should create successfully.

### 8. Task 8: Script to Load Initial Configuration to MongoDB
*   **Concern:** Persisting initial scraping target config.
*   **Start:** MongoDB is empty or has no relevant data for this MVP.
*   **Action:**
    *   Create a script `/self_learning_scraper/scripts/setup_initial_config.py`.
    *   In this script:
        ```python
        # /self_learning_scraper/scripts/setup_initial_config.py
        from self_learning_scraper.database.mongo_client import get_db_connection
        from self_learning_scraper.database.schemas import ScrapingTarget, FieldToExtract

        # Note: The Engineer LLM must replace "/full/path/to/" with the correct absolute path
        MVP_TARGET_ID = "mvp_test_page"
        MVP_TARGET_URL = "file:///full/path/to/self_learning_scraper/data/test_page.html"

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
        ```
*   **End:** `targets` collection in MongoDB contains one document matching the `ScrapingTarget` schema.
*   **Test:** Run `python self_learning_scraper/scripts/setup_initial_config.py`. Verify the document in MongoDB using a GUI or shell. Check structure and values, especially `_id`.

### 9. Task 9: Scraper Reads Configuration from MongoDB (`run_dynamic_scrape_v1.py`)
*   **Concern:** Decoupling scraper logic from hardcoded config.
*   **Start:** `run_manual_scrape_v1.py` uses hardcoded config.
*   **Action:**
    *   Create `/self_learning_scraper/run_dynamic_scrape_v1.py`.
    *   In this script:
        ```python
        # /self_learning_scraper/run_dynamic_scrape_v1.py
        import asyncio
        from self_learning_scraper.database.mongo_client import get_db_connection
        from self_learning_scraper.database.schemas import ScrapingTarget
        from self_learning_scraper.scraper_core.browser_manager import get_page_dom
        from self_learning_scraper.scraper_core.extraction_engine import extract_data_with_selector

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
        ```
*   **End:** `run_dynamic_scrape_v1.py` scrapes based on MongoDB config.
*   **Test:**
    1.  Run `python self_learning_scraper/scripts/setup_initial_config.py` to ensure config is correct with selector "h1".
    2.  Run `python self_learning_scraper/run_dynamic_scrape_v1.py`. It should print "My MVP Product Title".
    3.  Manually change `current_selector` in MongoDB for the `mvp_test_page` target's first field to "h2" (an invalid selector for the title).
    4.  Re-run `python self_learning_scraper/run_dynamic_scrape_v1.py`. It should print "Data not found using selector 'h2'".
    5.  Change selector back to "h1" in MongoDB.

---
## Phase 3: LLM Integration for Selector Suggestion

### 10. Task 10: Gemini API Client Setup (`llm_adapter/gemini_client.py`)
*   **Concern:** Basic communication with Gemini API.
*   **Start:** No LLM interaction. `google-generativeai` not installed.
*   **Action:**
    *   Add `google-generativeai` to `/self_learning_scraper/requirements.txt` and instruct to run `pip install -r requirements.txt`.
    *   In `/self_learning_scraper/config/settings.py`, add:
        ```python
        # /self_learning_scraper/config/settings.py
        # ... (MONGO_URI, DATABASE_NAME already exist)
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-pro") 
        ```
        (Engineer LLM will need to ensure `GEMINI_API_KEY` environment variable is set).
    *   Create `/self_learning_scraper/llm_adapter/gemini_client.py`.
    *   In `gemini_client.py`:
        ```python
        # /self_learning_scraper/llm_adapter/gemini_client.py
        from typing import Optional
        import google.generativeai as genai
        from self_learning_scraper.config import settings

        def get_llm_suggestion(prompt: str) -> Optional[str]:
            if not settings.GEMINI_API_KEY:
                print("Error: GEMINI_API_KEY not configured.")
                return None
            
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.LLM_MODEL_NAME)
                response = model.generate_content(prompt)
                
                # Basic check for response text, Gemini API might have specific error handling
                if response.parts:
                    return response.text # response.text is a convenience accessor
                else:
                    print(f"LLM Warning: Received no parts in response. Full response: {response}")
                    return None

            except Exception as e:
                print(f"Error during LLM suggestion: {e}")
                return None
        ```
*   **End:** `get_llm_suggestion` can send a prompt and get a response.
*   **Test:** In a temporary script, import `get_llm_suggestion` and call it: `response = get_llm_suggestion("Hello Gemini, what is the capital of France?")`. Print the response. (Ensure API key is correctly set in env).

### 11. Task 11: Prompt Template for Selector Suggestion (`llm_adapter/prompt_templates.py`)
*   **Concern:** Structuring the request to the LLM.
*   **Start:** No prompt defined for selector generation.
*   **Action:**
    *   Create `/self_learning_scraper/llm_adapter/prompt_templates.py`.
    *   Define a function `get_selector_suggestion_prompt(html_dom_segment: str, field_description: str) -> str`:
        ```python
        # /self_learning_scraper/llm_adapter/prompt_templates.py
        def get_selector_suggestion_prompt(html_dom_segment: str, field_description: str) -> str:
            # For MVP, keep DOM simplification minimal or send a relevant chunk.
            # A more robust version would simplify the DOM significantly.
            return f"""
Given the following HTML DOM segment:
--- HTML START ---
{html_dom_segment[:4000]} 
--- HTML END --- 
(Note: DOM might be truncated for brevity)

Suggest a single, robust CSS selector to extract the HTML element that best represents: "{field_description}".
Provide only the CSS selector string and nothing else. For example: div.product-name > span
If you cannot determine a selector, return "NO_SELECTOR_FOUND".
"""
        # Truncating DOM to avoid excessive token usage for MVP testing.
        # This limit should be configured or made more intelligent.
        ```
*   **End:** `get_selector_suggestion_prompt` function exists.
*   **Test:** Call it with some dummy HTML (e.g., content of `data/test_page.html`) and description, print the result to see the formatted prompt.

### 12. Task 12: LLM-based Selector Suggestion (`llm_adapter/dom_analyzer.py`)
*   **Concern:** Combining prompt generation and LLM call for selector suggestion.
*   **Start:** `llm_adapter/dom_analyzer.py` does not exist.
*   **Action:**
    *   Create `/self_learning_scraper/llm_adapter/dom_analyzer.py`.
    *   In `dom_analyzer.py`:
        ```python
        # /self_learning_scraper/llm_adapter/dom_analyzer.py
        from typing import Optional
        from .prompt_templates import get_selector_suggestion_prompt
        from .gemini_client import get_llm_suggestion

        def suggest_new_selector_from_dom(html_dom: str, field_description: str) -> Optional[str]:
            # For MVP, we might send the whole DOM if it's small (like test_page.html).
            # The prompt template already includes a truncation note.
            prompt = get_selector_suggestion_prompt(html_dom, field_description)
            raw_suggestion = get_llm_suggestion(prompt)

            if raw_suggestion:
                cleaned_suggestion = raw_suggestion.strip()
                if cleaned_suggestion == "NO_SELECTOR_FOUND" or not cleaned_suggestion:
                    return None
                # Further cleaning if LLM adds extra text like "CSS selector: "
                if cleaned_suggestion.lower().startswith("css selector:"):
                    cleaned_suggestion = cleaned_suggestion[len("css selector:"):].strip()
                if cleaned_suggestion.startswith("`") and cleaned_suggestion.endswith("`"): # Remove markdown backticks
                    cleaned_suggestion = cleaned_suggestion[1:-1]
                return cleaned_suggestion
            return None
        ```
*   **End:** `suggest_new_selector_from_dom` function exists.
*   **Test:**
    *   Fetch the DOM of `data/test_page.html` (e.g., using `browser_manager.get_page_dom`).
    *   Call `suggest_new_selector_from_dom(dom_content, "The main H1 title of the product")`.
    *   Print the result. It should hopefully be "h1" or a similar valid selector.

---
## Phase 4: Manual Re-learning Workflow Simulation

### 13. Task 13: Update Scraper Script for Failure Detection and State Update (`run_dynamic_scrape_v1.py`)
*   **Concern:** Identifying when the current selector fails and updating the `is_broken` status in MongoDB.
*   **Start:** `run_dynamic_scrape_v1.py` just prints if data not found.
*   **Action:**
    *   Modify `/self_learning_scraper/run_dynamic_scrape_v1.py` (additions marked):
        ```python
        # /self_learning_scraper/run_dynamic_scrape_v1.py
        # ... (imports and MVP_TARGET_ID remain the same)

        async def main():
            db = get_db_connection()
            targets_collection = db["targets"]
            config_dict = targets_collection.find_one({"_id": MVP_TARGET_ID})
            # ... (config loading and validation remain the same) ...
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
            
            field_to_extract = target_config.fields[0]
            url_to_scrape = target_config.url
            selector = field_to_extract.current_selector

            if not selector:
                print(f"No selector defined for field '{field_to_extract.name}'.")
                # Optionally mark as broken if selector is missing
                # targets_collection.update_one({"_id": MVP_TARGET_ID}, {"$set": {"is_broken": True}})
                return

            print(f"Attempting to scrape: {url_to_scrape} for field '{field_to_extract.name}' using selector '{selector}'")
            dom = await get_page_dom(url_to_scrape)
            scrape_successful = False # NEW

            if dom:
                extracted_data = extract_data_with_selector(dom, selector)
                if extracted_data:
                    print(f"Extracted data: {extracted_data}")
                    scrape_successful = True # NEW
                else:
                    print(f"Data not found using selector '{selector}'.")
            else:
                print("Failed to fetch DOM.")
            
            # Update is_broken status in MongoDB - NEW BLOCK
            if scrape_successful:
                if target_config.is_broken: # If it was broken, mark as fixed
                    targets_collection.update_one({"_id": MVP_TARGET_ID}, {"$set": {"is_broken": False}})
                    print(f"Target '{MVP_TARGET_ID}' marked as NOT broken.")
            else: # Scrape failed or data not found
                if not target_config.is_broken: # If it wasn't broken, mark as broken
                    targets_collection.update_one({"_id": MVP_TARGET_ID}, {"$set": {"is_broken": True}})
                    print(f"Target '{MVP_TARGET_ID}' marked as BROKEN.")
                else: # Already marked as broken
                    print(f"Target '{MVP_TARGET_ID}' remains BROKEN.")


        if __name__ == "__main__":
            asyncio.run(main())
        ```
*   **End:** `run_dynamic_scrape_v1.py` updates `is_broken` status in MongoDB based on scrape success.
*   **Test:**
    1.  Ensure `current_selector` for `mvp_test_page` in MongoDB is correct ("h1") and `is_broken` is `False` (run `setup_initial_config.py`). Run `run_dynamic_scrape_v1.py`. It should print data, and `is_broken` in MongoDB should remain `False`.
    2.  Manually change `current_selector` in MongoDB to "invalid-selector". Run `run_dynamic_scrape_v1.py`. It should print "Data not found...", and `is_broken` in MongoDB should now be `True`.
    3.  Manually change `current_selector` back to "h1". Run `run_dynamic_scrape_v1.py`. It should print data, and `is_broken` in MongoDB should now be `False`.

### 14. Task 14: Script for Manual Re-learning Trigger (`scripts/manual_relearn_trigger.py`)
*   **Concern:** A script to initiate the LLM-guided re-learning for a target marked as broken.
*   **Start:** No re-learning trigger script.
*   **Action:**
    *   Create `/self_learning_scraper/scripts/manual_relearn_trigger.py`.
    *   In this script:
        ```python
        # /self_learning_scraper/scripts/manual_relearn_trigger.py
        import asyncio
        from self_learning_scraper.database.mongo_client import get_db_connection
        from self_learning_scraper.database.schemas import ScrapingTarget
        from self_learning_scraper.scraper_core.browser_manager import get_page_dom
        from self_learning_scraper.llm_adapter.dom_analyzer import suggest_new_selector_from_dom

        MVP_TARGET_ID = "mvp_test_page"

        async def trigger_relearn():
            db = get_db_connection()
            targets_collection = db["targets"]
            
            config_dict = targets_collection.find_one({"_id": MVP_TARGET_ID})

            if not config_dict:
                print(f"Configuration for target_id '{MVP_TARGET_ID}' not found.")
                return
            
            target_config = ScrapingTarget(**config_dict)

            if not target_config.is_broken:
                print(f"Target '{MVP_TARGET_ID}' is not marked as broken. No re-learning needed now.")
                return

            print(f"Target '{MVP_TARGET_ID}' is broken. Attempting to find a new selector.")
            
            if not target_config.fields:
                print("No fields defined for this target.")
                return
            
            # MVP: Focus on the first field
            field_to_relearn = target_config.fields[0]
            
            print(f"Fetching current DOM for {target_config.url}...")
            current_dom = await get_page_dom(target_config.url)

            if current_dom:
                print(f"Attempting to suggest new selector for field: '{field_to_relearn.name}' ({field_to_relearn.description})")
                new_selector_suggestion = suggest_new_selector_from_dom(current_dom, field_to_relearn.description)

                if new_selector_suggestion:
                    print(f"\nLLM suggested new selector: '{new_selector_suggestion}'")
                    print(f"Old selector was: '{field_to_relearn.current_selector}'")
                    print("\nTo apply this suggestion:")
                    print(f"1. Manually update the 'current_selector' for field '{field_to_relearn.name}'")
                    print(f"   in the MongoDB document with _id '{MVP_TARGET_ID}' to '{new_selector_suggestion}'.")
                    print(f"2. Manually set 'is_broken' to false for this document.")
                    print(f"3. Re-run the scraper (run_dynamic_scrape_v1.py) to test.")
                else:
                    print("LLM could not suggest a new selector.")
            else:
                print(f"Could not fetch DOM for {target_config.url}. Re-learning aborted.")

        if __name__ == "__main__":
            asyncio.run(trigger_relearn())
        ```
*   **End:** `manual_relearn_trigger.py` can be run to get a selector suggestion for a broken target.
*   **Test:**
    1.  Ensure `mvp_test_page` in MongoDB has `is_broken: True` and an invalid selector (e.g., run `run_dynamic_scrape_v1.py` after setting an invalid selector, which will mark it broken).
    2.  Run `python self_learning_scraper/scripts/manual_relearn_trigger.py`.
    3.  It should fetch the DOM, call Gemini, print a suggested selector (hopefully "h1" or similar for `test_page.html`), and provide instructions for manual update.

### 15. Task 15: Final Manual Update and Verification Cycle
*   **Concern:** Completing the feedback loop manually as a developer/tester. This task is for the human interacting with the system.
*   **Start:** `manual_relearn_trigger.py` has printed a suggestion. The target is still marked `is_broken` with the old selector in DB.
*   **Action (Developer/Tester - Not a script for the LLM Engineer):**
    1.  Observe the `new_selector_suggestion` printed by `scripts/manual_relearn_trigger.py`.
    2.  **Manually** open MongoDB (using a GUI or shell like `mongosh`).
    3.  Find the `mvp_test_page` document in the `targets` collection of the `self_learning_scraper_db_mvp` database.
    4.  Update the `fields[0].current_selector` with the `new_selector_suggestion` (e.g., "h1").
    5.  Update the root `is_broken` field for the document to `false`.
    6.  Save changes in MongoDB.
    7.  Re-run `/self_learning_scraper/run_dynamic_scrape_v1.py`.
*   **End:** The `run_dynamic_scrape_v1.py` script works again using the LLM-suggested selector and updates `is_broken` to `False` (if it was previously true) on successful scrape.
*   **Test:** `run_dynamic_scrape_v1.py` should now successfully extract and print "My MVP Product Title". The `is_broken` flag for `mvp_test_page` in MongoDB should be `false`.