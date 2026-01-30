import threading
import requests
from lxml import html

from app.models import Product

SESSION = requests.Session()


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
}


websites = [
    'https://www.vendr.com/marketplace/mulesoft'
]


def fetch_html(url: str) -> str:
    r = SESSION.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text


def parse_product_name(tree) -> str:
    name = tree.xpath("normalize-space((//h1)[1])")
    return name or None

def parse_product_median_price(tree):
    median = tree.xpath("//text()[contains(., 'Median')]/following::text()[contains(., '$')][1]")
    return median[0].strip() if median else None


def parse_low_high(tree):
    low_node = tree.xpath("//*[normalize-space()='Low']")
    if not low_node:
        return None, None

    grids = low_node[0].xpath("preceding::div[.//text()[contains(., '$')]][1]")
    if not grids:
        return None, None

    prices = grids[0].xpath(".//text()[contains(., '$')]")
    prices = [p.strip() for p in prices if p.strip()]

    if len(prices) >= 2:
        return prices[0], prices[-1]
    return None, None

def parse_description(tree):
    desc = tree.xpath(
        "//h3[contains(., 'Overview')]/following::p[1]/text()"
    )
    return desc[0].strip() if desc else None


def scrape_product_page(url: str):
    try:
        html_text = fetch_html(url)
        tree = html.fromstring(html_text)
        prod = parse_product(tree)
        print(prod)
        return prod
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def multithread_scraping():
    threads = []
    for url in websites:
        thread = threading.Thread(target=scrape_product_page, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def parse_product(tree) -> Product:
    low, high = parse_low_high(tree)
    return Product(
        product_name=parse_product_name(tree),
        low_price=low,
        median_price=parse_product_median_price(tree),
        high_price=high,
        description=parse_description(tree),
    )


if __name__ == "__main__":
    multithread_scraping()