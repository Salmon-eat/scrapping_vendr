import queue
import threading

import requests
from lxml import html

from app.HEADER import SESSION
from app.db import Base, SessionLocal, engine
from app.scrapping_product.scrapping_product import ProductParser
from app.scrapping_products_category.scrapping_url_products import CategoryParsing
from logging_config import logger

task_queue = queue.Queue(maxsize=100)
db_queue = queue.Queue()

CATEGORY_URLS = [
    "https://www.vendr.com/categories/devops",
    "https://www.vendr.com/categories/it-infrastructure",
    "https://www.vendr.com/categories/data-analytics-and-management",
]


def worker():
    session = requests.Session()
    parser = ProductParser(session=session)
    while True:
        task = task_queue.get()
        if task is None:
            logger.info("Worker shutting down")
            task_queue.task_done()
            break
        url, part_name = task
        try:
            product_data = parser.scrape_product_page(url, part_name)
            if product_data:
                db_queue.put(product_data)
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        finally:
            task_queue.task_done()


def db_writer():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        while True:
            product_data = db_queue.get()
            if product_data is None:
                db_queue.task_done()
                break

            try:
                session.add(product_data)
                session.commit()
            except Exception as e:
                logger.error(f"Database commit failed: {e}")
                session.rollback()
            finally:
                db_queue.task_done()
    finally:
        session.close()


def main():
    logger.info("Starting Scraper")
    writer_thread = threading.Thread(target=db_writer, daemon=True)
    writer_thread.start()

    worker_threads = []
    for _ in range(5):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        worker_threads.append(t)

    shared_session = requests.Session()
    category_tool = CategoryParsing(session=SESSION)

    for path in CATEGORY_URLS:
        try:
            response = shared_session.get(path, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to load {path} Status: {response.status_code}")

            category_tree = html.fromstring(response.content)
            url_categories = category_tree.xpath(
                "//a[contains(@href, '/it-infrastructure/')]/@href"
            )
            part_name = category_tool.parse_category_name(category_tree)

            for prod_url in category_tool.product_links_generator(url_categories):
                task_queue.put((prod_url, part_name))
        except Exception as e:
            logger.error(f"Error in main category: {e}")

    task_queue.join()

    for _ in range(5):
        task_queue.put(None)
    for t in worker_threads:
        t.join()

    db_queue.put(None)
    writer_thread.join()


if __name__ == "__main__":
    main()
