from typing import Generator

from lxml import html

from app.HEADERS import fetch_html

BASE = "https://www.vendr.com"
CATEGORY_PATH = "/categories/it-infrastructure/api"


def parse_category_name(category_tree) -> str:
    return category_tree.xpath("normalize-space((//h1)[1])") or None


def product_links_generator() -> Generator[str, None, None]:
    page = 1
    while True:
        page_url = f"{BASE}{CATEGORY_PATH}?page={page}"
        tree = html.fromstring(fetch_html(page_url))

        links = tree.xpath("//a[contains(@href, '/marketplace/')]/@href")
        if not links:
            break

        for href in links:
            yield BASE + href

        page += 1
