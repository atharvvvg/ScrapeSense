# Self-Learning Web Scraper with LLM & RL Integration

**Problem Solved:** Web scrapers break when website structure changes.
**Project Goal:** An AI-enhanced scraper that re-learns how to extract information when structure changes, using LLMs to guide it based on DOM trees, and RL to optimize adaptation.

**Tech Stack:**

- **Core:** Python
- **Web Interaction:** Selenium / Playwright (Playwright is generally faster and more modern)
- **LLM:** Google Gemini API
- **Database:** MongoDB (for DOMs, extracted data, configurations, RL states)
- **Orchestration/Task Queue (Optional but Recommended for Scale):** Celery with RabbitMQ/Redis
- **API (Optional, for external control/monitoring):** FastAPI / Flask
- **RL Library (Optional):** Stable Baselines3, RLlib, or custom implementation for simpler cases.

---

## I. High-Level Architecture Overview

The system will operate in a few key phases:

1.  **Initial Setup & Scrape:** User defines target URL and data points to extract (e.g., "product name," "price," "description"). The LLM helps generate initial selectors.
2.  **Monitoring & Change Detection:** The scraper runs periodically. If extraction fails or data quality degrades, a change is detected.
3.  **Re-learning (LLM-Guided):**
    - The current DOM is fetched.
    - The LLM (Gemini) is prompted with the simplified DOM, the target data description (e.g., "Find the main price of the product"), and potentially the old (broken) selectors.
    - The LLM suggests new candidate selectors or extraction strategies.
4.  **Validation & Update:** The new selectors are tested. If successful, the configuration is updated.
5.  **Reinforcement Learning (RL) Feedback Loop (Advanced):**
    - The process of selecting/generating selectors is framed as an RL problem.
    - **State:** Simplified DOM representation, previous selectors, success/failure history.
    - **Action:** Choose a strategy to generate new selectors (e.g., ask LLM with a specific prompt, try variations of old selectors, use a different LLM approach).
    - **Reward:** Positive reward for successful, accurate, and robust extraction; negative reward for failures or poor-quality data.
    - The RL agent learns to choose better adaptation strategies over time.

---

## II. File and Folder Structure

```
/self_learning_scraper
|
|-- /scraper_core
| |-- init.py
| |-- browser_manager.py # Manages Playwright/Selenium browser instances
| |-- scraper_agent.py # Core agent that performs scraping, uses selectors
| |-- extraction_engine.py # Applies selectors, extracts and cleans data
| |-- change_detector.py # Detects if scraper is broken or data quality is low
|
|-- /llm_adapter
| |-- init.py
| |-- gemini_client.py # Interface for Gemini API
| |-- dom_analyzer.py # Uses LLM to analyze DOM and suggest selectors
| |-- prompt_templates.py # Stores various prompt templates for LLM
|
|-- /relearning_manager
| |-- init.py
| |-- manager.py # Orchestrates the re-learning process
|
|-- /rl_agent (Advanced)
| |-- init.py
| |-- agent.py # RL agent (e.g., Q-learning, Policy Gradient)
| |-- environment.py # Defines the RL environment (state, action, reward)
| |-- models.py # Neural network models for the RL agent (if using deep RL)
|
|-- /database
| |-- init.py
| |-- mongo_client.py # MongoDB connection and utility functions
| |-- schemas.py # Pydantic models for data validation & DB structure
|
|-- /orchestration (Optional, for Celery)
| |-- init.py
| |-- tasks.py # Celery tasks (e.g., scheduled_scrape, relearn_task)
| |-- celery_app.py # Celery application setup
|
|-- /api (Optional, for FastAPI/Flask)
| |-- init.py
| |-- main.py # FastAPI/Flask application entry point
| |-- routes.py # API endpoints (e.g., to trigger scrapes, view status)
|
|-- /config
| |-- init.py
| |-- settings.py # Application settings (API keys, DB URI, etc.)
| |-- scraping_targets.json # Initial definitions of websites and data to scrape
|
|-- /utils
| |-- init.py
| |-- dom_utils.py # Functions for cleaning, simplifying, or hashing DOMs
| |-- logging_config.py # Logging setup
|
|-- /logs # Log files
|-- /data # Potentially store large DOM snapshots or outputs
|
|-- main.py # Main entry point to start services or scheduler
|-- requirements.txt
|-- README.md
```

## III. What Each Part Does

**1. `/scraper_core`**
_ **`browser_manager.py`**:
_ Initializes and manages browser instances (e.g., Playwright browser contexts).
_ Handles browser launch, navigation, and cleanup.
_ Provides a way to get the current page's DOM.
_ **`scraper_agent.py`**:
_ Takes a target URL and a set of selectors (or extraction rules).
_ Uses `browser_manager` to navigate and fetch the page.
_ Passes the DOM and selectors to `extraction_engine`.
_ Returns extracted data or error status.
_ **`extraction_engine.py`**:
_ Receives a DOM (or page object) and selectors/rules.
_ Applies CSS selectors, XPath, or other rules to extract specific data elements.
_ Performs basic data cleaning (e.g., stripping whitespace, converting types).
_ Validates extracted data against expected formats (e.g., price should be a number).
_ **`change_detector.py`**:
_ Compares current scraping results against a baseline or expected output.
_ Checks for:
_ Empty results for previously yielding selectors.
_ Significant changes in data format.
_ Hashing the relevant parts of the DOM and comparing to a previous "good" hash. \* Triggers the re-learning process if a significant change is detected.

**2. `/llm_adapter`**
_ **`gemini_client.py`**:
_ Handles authenticated communication with the Google Gemini API.
_ Sends prompts and receives responses.
_ Manages API rate limits and error handling.
_ **`dom_analyzer.py`**:
_ Takes a (potentially simplified) DOM string, target data descriptions (e.g., "product title," "price"), and optionally old/broken selectors.
_ Uses `prompt_templates` to construct effective prompts for Gemini.
_ Example Prompt: "Given this HTML DOM, identify the CSS selector for the main product price. The price is usually near the product title and has a currency symbol. Old selector was 'span.price-old'. DOM: <simplified_dom_tree>"
_ Parses Gemini's response to extract candidate selectors or extraction logic.
_ **`prompt_templates.py`**: \* Stores and manages various prompt templates for different scenarios (initial selector generation, re-learning, DOM summarization).

**3. `/relearning_manager`**
_ **`manager.py`**:
_ Orchestrates the re-learning flow when triggered by `change_detector`.
_ Coordinates fetching the new DOM via `scraper_core.browser_manager`.
_ Invokes `llm_adapter.dom_analyzer` to get new selector candidates.
_ Tests candidate selectors using `scraper_core.extraction_engine` on the current DOM.
_ If successful, updates the scraping configuration in MongoDB for that target. \* If RL is active, it interacts with the `rl_agent` to decide on the re-learning strategy and provide feedback.

**4. `/rl_agent` (Advanced)**
_ **`environment.py`**:
_ Defines the scraper's adaptation problem as an RL environment.
_ **State:** Could include a featurized representation of the DOM (e.g., tag counts, depth, presence of certain keywords near target), history of selector success/failure for this site, current (broken) selectors, and the LLM's confidence/ambiguity.
_ **Actions:** Could be:
_ "Ask LLM with generic prompt."
_ "Ask LLM with prompt including old selectors."
_ "Ask LLM to focus on visual cues (if DOM includes them)."
_ "Try small variations of old selectors (e.g., parent, sibling)."
_ "Request human intervention (if configured)."
_ **Reward Function:**
_ `+R_success` for successful extraction of all target fields.
_ `+R_partial` for partial success.
_ `-R_failure` for complete failure.
_ `-R_cost` for LLM API calls or computation time.
_ `+R_robustness` if the new selector works across minor page variations (harder to measure directly without historical data or simulated changes).
_ **`agent.py`**:
_ Implements an RL algorithm (e.g., Q-Learning for discrete action spaces, or a policy gradient method if actions are more complex).
_ Learns a policy `π(action | state)` that maximizes expected future rewards.
_ Its `act()` method chooses an action based on the current state.
_ Its `learn()` method updates its knowledge based on the (state, action, reward, next_state) tuple. \* **`models.py`**: If using Deep RL, this would contain PyTorch/TensorFlow models for Q-functions or policies.

**5. `/database`**
_ **`mongo_client.py`**:
_ Handles connection to MongoDB.
_ Provides CRUD (Create, Read, Update, Delete) operations for various collections.
_ **`schemas.py`**:
_ Defines Pydantic models for data structures stored in MongoDB. This ensures data integrity and provides clear schemas. Examples:
_ `ScrapingTargetConfig`: URL, data fields (name, description, current selector, type), last successful scrape timestamp, history of selectors.
_ `ExtractedData`: Target ID, scraped timestamp, data dictionary.
_ `DOMSnapshot`: Target ID, timestamp, HTML content (or simplified representation). \* `RLStateActionReward`: For storing RL training data.

**6. `/orchestration` (Celery)**
_ **`celery_app.py`**: Configures the Celery application, broker (RabbitMQ/Redis), and backend.
_ **`tasks.py`**:
_ `scheduled_scrape_task(target_id)`: A Celery task to perform a regular scrape for a given target.
_ `relearn_task(target_id)`: A Celery task triggered when a change is detected. \* These tasks would use the components from `scraper_core`, `relearning_manager`, etc.

**7. `/api` (FastAPI/Flask)**
_ **`main.py`**: Initializes the API application.
_ **`routes.py`**: Defines API endpoints:
_ `POST /targets`: Add a new scraping target.
_ `GET /targets/{target_id}`: Get status/config of a target.
_ `POST /targets/{target_id}/scrape`: Trigger an immediate scrape.
_ `GET /data/{target_id}`: Retrieve extracted data.

**8. `/config`**
_ **`settings.py`**:
_ Loads sensitive information (API keys, database URI) from environment variables or a `.env` file.
_ Global constants, LLM model choice, retry counts, etc.
_ **`scraping_targets.json`**:
_ An initial JSON file defining websites to scrape and what data to look for.
_ Example: `{"url": "example.com/product/123", "fields": [{"name": "product_name", "description": "The main title of the product"}, {"name": "price", "description": "The current selling price"}]}` \* This would be loaded into MongoDB on first run.

**9. `/utils`**
_ **`dom_utils.py`**:
_ Functions to simplify HTML DOMs (e.g., remove scripts, styles, comments, unnecessary attributes). This makes the DOM smaller and easier for the LLM to process, reducing token usage and improving focus.
_ Could also include functions to convert HTML to a more structured format (e.g., JSON-like tree) or to generate DOM "fingerprints" for change detection.
_ **`logging_config.py`**: Centralized configuration for logging.

**10. `main.py` (Root level)**
_ The main entry point for the application.
_ Could start a scheduler (like `APScheduler` if not using Celery) to run scraping jobs.
_ If using Celery, this might not be used, and Celery workers would be started separately.
_ If using an API, this would start the API server.

---

## IV. Where State Lives & How Services Connect

**A. State Management:**

- **MongoDB is the primary state store:**

  - **Scraping Configurations:**

    - `targets` collection: Stores details for each website (URL, fields to extract, current working selectors, history of selectors, last successful scrape, status).
    - Schema example (from `database/schemas.py`):

      ```python
      class FieldToExtract(BaseModel):
          name: str  # e.g., "product_title"
          description: str  # "The main H1 title of the product"
          current_selector: Optional[str] = None # CSS or XPath
          selector_type: Optional[str] = None # "css", "xpath", "llm_instruction"
          history: List[Tuple[str, datetime]] = [] # (selector, timestamp_it_worked_until)

      class ScrapingTarget(BaseModel):
          id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
          url: str
          fields: List[FieldToExtract]
          last_scraped_successfully: Optional[datetime] = None
          is_broken: bool = False
          # ... other metadata
      ```

  - **Extracted Data:**
    - `extracted_data` collection: Stores the data scraped from websites, linked to the target and timestamp.
  - **DOM Snapshots (Optional but useful for re-learning):**
    - `dom_snapshots` collection: Stores (potentially simplified) DOMs, especially when a change is detected or for training the RL agent.
  - **LLM Interaction Logs:**
    - `llm_interactions` collection: Prompts sent to Gemini and responses received, useful for debugging and fine-tuning prompts.
  - **RL Agent State (If applicable):**
    - `rl_models` collection: If the RL agent has a model (e.g., Q-table, neural network weights), it's stored here.
    - `rl_experience` collection: Stored (state, action, reward, next_state) tuples for training.

- **In-memory State (Transient):**
  - Current browser page DOM within `ScraperAgent` during a scrape.
  - Variables within functions during execution.

**B. Service Connections & Data Flow:**

1.  **Scheduler (APScheduler in `main.py` or Celery Worker):**

    - Pulls `ScrapingTarget` configurations from MongoDB.
    - For each target, initiates a scrape job.

2.  **Scrape Job (`ScraperAgent`):**

    - Receives target URL and `current_selector`s from the job trigger.
    - Uses `BrowserManager` to fetch the page DOM.
    - Uses `ExtractionEngine` to apply selectors to the DOM.
    - **Success:** Stores extracted data in `extracted_data` (MongoDB). Updates `last_scraped_successfully` for the target in MongoDB.
    - **Failure/Change Detected (`ChangeDetector`):**
      - `ChangeDetector` compares current results/DOM with past state (from MongoDB or in-memory cache of last good state).
      - If change detected, sets `is_broken = True` for the target in MongoDB.
      - Triggers the `ReLearningManager`.

3.  **Re-learning (`ReLearningManager`):**

    - Reads the broken `ScrapingTarget` config from MongoDB.
    - Fetches the current "problematic" DOM using `BrowserManager`.
    - **RL Interaction (if enabled):**
      - The `RLAgent.environment` creates a state representation.
      - `RLAgent.agent` chooses an action (e.g., which prompt strategy for LLM).
    - Sends the DOM, field descriptions, and potentially the chosen strategy to `DOMAnalyzer` (`LLMAdapter`).
    - `DOMAnalyzer` queries Gemini via `GeminiClient`.
    - Receives candidate selectors from Gemini.
    - Tests candidate selectors using `ExtractionEngine` on the current DOM.
    - **If new selectors work:**
      - Updates `current_selector` and `history` for the fields in the `ScrapingTarget` (MongoDB).
      - Sets `is_broken = False`.
      - Logs the successful re-learning.
      - Provides positive reward to `RLAgent`.
    - **If new selectors fail:**
      - Logs failure.
      - Provides negative reward to `RLAgent`.
      - May try another RL action or escalate (e.g., notify admin).

4.  **Data Flow into MongoDB:**

    - `ScraperAgent` -> `extracted_data`
    - `ChangeDetector` / `ReLearningManager` -> update `targets` (status, selectors)
    - `LLMAdapter` -> `llm_interactions` (prompts, responses)
    - `ReLearningManager` (via `BrowserManager`) -> `dom_snapshots` (on failure)
    - `RLAgent` -> `rl_models`, `rl_experience`

5.  **API Layer (FastAPI/Flask - Optional):**
    - Reads/writes to MongoDB for managing targets, viewing data, or triggering actions.
    - Provides a user interface or programmatic access to the system.

**Visual Flow (Simplified):**

```
+-----------+ 1. Get Target +-------------+
| Scheduler |---------------------->| MongoDB |
+-----------+ | (Targets) |<---+
| +-------------+ | 6. Update
| 2. Trigger Scrape | Config/Status
v |
+---------------+ 3. Fetch DOM +-----------------+ |
| Scraper Agent |----------------->| Target Website | |
+---------------+ +-----------------+ |
| | ^ |
| | | 5b. Test New Selectors |
| | +-----------------------+ |
| | | |
v | 4a. Data OK? Store. | |
+-----------------+ <----------------+ |
| Change Detector | |
+-----------------+ |
| 4b. Data BAD! Trigger Relearn |
v |
+---------------------+ 5a. Analyze DOM +--------------+
| Relearning Manager |-------------------->| LLM Adapter |
| (with RL Agent opt.)| | (Gemini) |
+---------------------+-------------------->+--------------+
```

## V. Advanced Considerations & Challenges

- **DOM Simplification:** Crucial for LLMs. Raw DOMs are too verbose. Remove scripts, styles, comments, irrelevant attributes. Consider converting parts of the DOM to a more structured representation (e.g., Markdown-like or JSON) before sending to the LLM.
- **Prompt Engineering:** The quality of LLM output heavily depends on prompts. Experiment with different phrasings, few-shot examples, and providing context (like old selectors).
- **Cost Management:** LLM API calls can be expensive. Optimize DOM simplification and prompt design. Implement caching for similar DOM structures if feasible. The RL agent could be rewarded for finding solutions with fewer LLM calls.
- **Robustness of Selectors:** LLMs might generate very specific selectors that are brittle. Encourage generation of more robust selectors (e.g., based on ARIA roles, data attributes, or relative positioning). The RL agent could learn this.
- **Feedback Granularity for RL:** Defining a good reward function is key. Is success binary, or can you measure the "quality" of extracted data?
- **Exploration vs. Exploitation in RL:** The RL agent needs to explore different re-learning strategies but also exploit ones that work well.
- **Human-in-the-Loop:** For very complex sites or persistent failures, the system might need a way to flag for human review. The human's solution can then be used as training data.
- **Scalability:** If scraping many sites frequently, a distributed task queue (Celery + RabbitMQ/Redis) is essential. Browser instances can be resource-intensive.
- **Anti-Scraping Measures:** Websites employ techniques to block scrapers (CAPTCHAs, IP blocking, browser fingerprinting). Playwright/Selenium help, but proxies, CAPTCHA solving services, and more sophisticated evasion techniques might be needed (outside the scope of the self-healing logic but important for the scraper itself).
- **Defining "Change":** How sensitive should the `ChangeDetector` be? Too sensitive, and it re-learns too often (costly). Not sensitive enough, and you get bad data. This might be a tunable parameter.
