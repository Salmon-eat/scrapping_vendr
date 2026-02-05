from typing import Optional, Tuple
from lxml import html

from app.HEADER import SESSION, HEADER
from app.models import Product
from logging_config import logger


class ProductParser:

    def __init__(self, session = None) -> None:
        self.session = session or SESSION
        self.session.headers.update(HEADER)

    def only_digits(self, element: str) -> str:
        if not element:
            return ""
        return "".join(s for s in element if s.isdigit())

    def parse_product_name(self, tree: html.HtmlElement) -> Optional[str]:
        name = tree.xpath("normalize-space((//h1)[1])")
        return name if name else None

    def parse_product_median_price(self, tree: html.HtmlElement) -> Optional[int]:
        median = tree.xpath(
            "//span[contains(text(), 'Median')]" "/following-sibling::text()"
        )
        if median:
            price = self.only_digits(median[0])
            return int(price) if price else None
        return None

    def parse_low_high(
        self, tree: html.HtmlElement
    ) -> Tuple[Optional[int], Optional[int]]:
        slider_container = tree.xpath("//div[contains(@class, '_rangeSlider')]")
        if not slider_container:
            return None, None

        prices = slider_container[0].xpath(".//span[contains(text(), '$')]/text()")

        if len(prices) >= 2:
            price_low, price_high = self.only_digits(prices[0]), self.only_digits(
                prices[1]
            )
            price_low = int(price_low) if price_low else None
            price_high = int(price_high) if price_high else None

            return price_low, price_high
        return None, None

    def parse_description(self, tree: html.HtmlElement) -> Optional[str]:
        desc = tree.xpath("//h3[contains(., 'Overview')]/following::p[1]/text()")
        return desc[0].strip() if desc else None

    def parse_product(self, tree: html.HtmlElement, category_name: str) -> Product:
        low, high = self.parse_low_high(tree)
        return Product(
            product_name=self.parse_product_name(tree),
            category=category_name,
            low_price=low,
            median_price=self.parse_product_median_price(tree),
            high_price=high,
            description=self.parse_description(tree),
        )

    def scrape_product_page(self, url: str, category_name: str) -> Optional[Product]:
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch {url}: Status {response.status_code}")
                return None

            tree = html.fromstring(response.content)
            return self.parse_product(tree, category_name)
        except Exception as e:
            logger.error(f"Error scraping product page {url}: {e}")
            return None
