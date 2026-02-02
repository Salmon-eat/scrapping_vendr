import threading
from concurrent.futures.thread import ThreadPoolExecutor

from lxml import html
from app.HEADERS import fetch_html
from app.scrapping_product.scrapping_product import scrape_product_page
from app.scrapping_products_category.scrapping_url_products import parse_category_name, product_links_generator

category_urls = "https://www.vendr.com/categories/it-infrastructure/api?page=1"

products =[]

def thread_execution(url, category_name):
    try:
        prod = scrape_product_page(url, category_name)
        products.append(prod)
        print(prod)
    except Exception as e:
        print(f"[ERROR] {url}: {e}")


def main():
    category_html = fetch_html(category_urls)
    category_tree = html.fromstring(category_html)
    category_name = parse_category_name(category_tree)
    with ThreadPoolExecutor(max_workers=5) as e:
        for url in product_links_generator():
            e.submit(thread_execution, url, category_name)


if __name__ == "__main__":
    main()