from typing import Generator, List, Optional

import requests
from lxml import html

from app.HEADER import SESSION, HEADER
from logging_config import logger


class CategoryParsing:
    BASE = "https://www.vendr.com"

    def __init__(self, session=None) -> None:
        self.session = session or SESSION
        self.session.headers.update(HEADER)

    def parse_category_name(self, tree: html.HtmlElement) -> Optional[str]:
        try:
            name = tree.xpath("normalize-space((//h1)[1])")
            return name if name else None
        except Exception as e:
            logger.error(f"Error parsing category name: {e}")
            return None

    def product_links_generator(
        self, url_categories: List[str]
    ) -> Generator[str, None, None]:
        for url in url_categories:
            url = url[:-1]
            page = 1
            while True:
                page_url = f"{self.BASE}{url}{page}"
                try:
                    response = self.session.get(page_url, timeout=10)

                    if response.status_code != 200:
                        logger.info(
                            f"End of pagination at page {page} (Status {response.status_code})"
                        )
                        break

                    tree = html.fromstring(response.content)
                    links = tree.xpath("//a[contains(@href, '/marketplace/')]/@href")
                    if not links:
                        logger.info(f"No more links on page {page}")
                        break

                    for href in links:
                        yield self.BASE + href

                    page += 1
                except requests.exceptions.RequestException as e:
                    logger.error(f"Network error on {page_url}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error on {page_url}: {e}")
                    break
