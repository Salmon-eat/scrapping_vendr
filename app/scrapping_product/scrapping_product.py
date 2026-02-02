
from lxml import html

from app.HEADERS import fetch_html
from app.models import Product



def parse_product_name(tree) -> str:
    name = tree.xpath("normalize-space((//h1)[1])")
    return name or None


def only_digits(element: str) -> str:
    return "".join(s for s in element if s.isdigit())


def parse_product_median_price(tree) -> int|None:
    median = tree.xpath("//span[contains(text(), 'Median')]/following-sibling::text()")
    if median:
        price = only_digits(median[0])
        return int(price)
    else:
        return None


def parse_low_high(tree) -> int|tuple:
    slider_container = tree.xpath("//div[contains(@class, '_rangeSlider')]")
    if not slider_container:
        return None, None

    prices = slider_container[0].xpath(".//span[contains(text(), '$')]/text()")
    price_low, price_high = only_digits(prices[0]), only_digits(prices[1])

    if len(prices) >= 2:
        return int(price_low), int(price_high)
    return None, None


def parse_description(tree):
    desc = tree.xpath(
        "//h3[contains(., 'Overview')]/following::p[1]/text()"
    )
    return desc[0].strip() if desc else None


def scrape_product_page(url: str, category_name):
    try:
        html_text = fetch_html(url)
        tree = html.fromstring(html_text)
        prod = parse_product(tree, category_name)
        return prod
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


def parse_product(tree, category_name: str) -> Product:
    low, high = parse_low_high(tree)
    return Product(
        product_name=parse_product_name(tree),
        category=category_name,
        low_price=low,
        median_price=parse_product_median_price(tree),
        high_price=high,
        description=parse_description(tree),
    )
