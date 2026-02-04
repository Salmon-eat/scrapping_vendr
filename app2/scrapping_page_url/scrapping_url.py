from typing import Generator

from playwright.sync_api import sync_playwright

BASE = "https://books.toscrape.com/"


def book_product_links_generator() -> Generator[str, None, None]:
    all_links = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_page = browser.new_page()
        page = 1
        while True:
            page_url = f"{BASE}catalogue/page-{page}.html"
            try:
                response = browser_page.goto(page_url, timeout=15000)
                if response.status != 200:
                    break
                book_link = browser_page.locator("h3 a").evaluate_all(
                    "elements => elements.map(el => el.href)"
                )
                all_links.extend(book_link)
                for url in book_link:
                    yield url
                page += 1
            except Exception as e:
                print(f"An error occurred: {e}")
        browser.close()
