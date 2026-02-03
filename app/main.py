import queue
import threading

from lxml import html

from app.db import Base, SessionLocal, engine
from app.HEADERS import fetch_html
from app.scrapping_category.scrapping_category import categories
from app.scrapping_product.scrapping_product import scrape_product_page
from app.scrapping_products_category.scrapping_url_products import (
    parse_category_name,
    product_links_generator,
)

task_queue = queue.Queue(maxsize=100)
db_queue = queue.Queue()

CATEGORY_URLS = [
    "https://www.vendr.com/categories/devops",
    "https://www.vendr.com/categories/it-infrastructure",
    "https://www.vendr.com/categories/data-analytics-and-management",
]


def worker():
    while True:
        task = task_queue.get()
        if task is None:
            task_queue.task_done()
            break
        url, part_name = task
        try:
            product_data = scrape_product_page(url, part_name)
            if product_data:
                db_queue.put(product_data)
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
                session.rollback()
            finally:
                db_queue.task_done()
    finally:
        session.close()


def main():
    writer_thread = threading.Thread(target=db_writer, daemon=True)
    writer_thread.start()

    worker_threads = []
    for _ in range(5):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        worker_threads.append(t)

    for path in CATEGORY_URLS:
        category_html = fetch_html(path)
        if not category_html:
            continue
        category_tree = html.fromstring(category_html)
        url_categories = categories(category_tree)
        part_name = parse_category_name(category_tree)

        for prod_url in product_links_generator(url_categories):
            task_queue.put((prod_url, part_name))

    task_queue.join()

    for _ in range(5):
        task_queue.put(None)
    for t in worker_threads:
        t.join()

    db_queue.put(None)
    writer_thread.join()


if __name__ == "__main__":
    main()
