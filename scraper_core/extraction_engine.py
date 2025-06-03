# /ScrapeSense/scraper_core/extraction_engine.py
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