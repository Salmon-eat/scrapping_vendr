from typing import Generator

from playwright.sync_api import Page, sync_playwright

from logging_config import logger


class LinkGenerator:
    BASE = "https://books.toscrape.com/"

    def __init__(self, headless: bool = True):
        self.headless = headless

    def product_links(self) -> Generator:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            browser_page = browser.new_page()
            page = 1
            while True:
                url = self._build_page_url(page)
                logger.info(f"Scraping page {page} for links")
                if not self._process_page(browser_page, url):
                    break

                links = self._extract_links(browser_page)
                for link in links:
                    yield link

                page += 1
            browser.close()

    def _build_page_url(self, page: int) -> str:
        return f"{self.BASE}catalogue/page-{page}.html"

    def _process_page(self, page: Page, url: str) -> bool:
        try:
            response = page.goto(url, timeout=15000)
            return response.status == 200
        except Exception as e:
            logger.error(f"Failed to load {url}: {e}")
            return False

    def _extract_links(self, page: Page) -> list[str]:
        return page.locator("h3 a").evaluate_all(
            "elements => elements.map(el => el.href)"
        )


def book_product_links_generator() -> Generator:
    crawler = LinkGenerator()
    return crawler.product_links()
