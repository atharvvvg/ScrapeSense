# /ScrapeSense/scraper_core/browser_manager.py
from playwright.async_api import async_playwright

async def get_page_dom(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
        return content 