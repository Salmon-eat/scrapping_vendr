from typing import Dict, Optional

from playwright.sync_api import Page

from app2.models import Book
from logging_config import logger


class BookParser:
    RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def __init__(self, page: Page) -> None:
        self.page = page

    def _parse_rating(self) -> int:
        rating_element = self.page.locator(".product_main .star-rating")
        rating_class = rating_element.get_attribute("class") or ""
        rating_word = rating_class.replace("star-rating ", "").strip()
        return self.RATING_MAP.get(rating_word, 0)

    def _parse_description(self) -> str:
        try:
            selector = "//div[@id='product_description']/following-sibling::p"
            return self.page.locator(selector).inner_text(timeout=3000)
        except Exception:
            logger.error("Description not found")
            return "No description available"

    def _parse_product_information(self) -> Dict[str, str]:
        info_data = {}
        rows = self.page.locator("table.table-striped tr").all()

        for row in rows:
            key = row.locator("th").inner_text().strip()
            value = row.locator("td").inner_text().strip()
            info_data[key] = value

        return info_data

    def _parse_price(self, price_str: str) -> float:
        return float(price_str.replace("£", "").strip())

    def _format_image_url(self) -> str:
        img_src = self.page.locator(".item.active img").get_attribute("src") or ""
        return img_src.replace("../../", "https://books.toscrape.com/")

    def parse(self) -> Optional[Book]:
        try:
            main_info = self.page.locator(".product_main")

            return Book(
                title=main_info.locator("h1").inner_text(),
                category=self.page.locator(".breadcrumb li")
                .nth(2)
                .inner_text()
                .strip(),
                price=self._parse_price(main_info.locator(".price_color").inner_text()),
                rating=self._parse_rating(),
                stock_availability=main_info.locator(".instock.availability")
                .inner_text()
                .strip(),
                image_url=self._format_image_url(),
                description=self._parse_description(),
                product_information=self._parse_product_information(),
            )
        except Exception as e:
            logger.error(f"Error parsing book: {e}")
            return None


def parse_book(page: Page) -> Optional[Book]:
    parser = BookParser(page)
    return parser.parse()
