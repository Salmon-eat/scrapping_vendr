from typing import Generator

from lxml import html

from app.HEADERS import fetch_html

BASE = "https://www.vendr.com"


def parse_category_name(category_tree) -> str:
    return category_tree.xpath("normalize-space((//h1)[1])") or None


def product_links_generator(url_categories) -> Generator[str, None, None]:
    for url in url_categories:
        url = url[:-1]
        page = 1
        while True:

            page_url = f"{BASE}{url}{page}"
            html_content = fetch_html(page_url)

            if html_content is None:
                break
            tree = html.fromstring(html_content)

            links = tree.xpath("//a[contains(@href, '/marketplace/')]/@href")
            if not links:
                break

            for href in links:
                yield BASE + href

            page += 1
