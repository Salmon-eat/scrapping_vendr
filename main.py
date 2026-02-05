import multiprocessing
import queue
import time
from app2.db import SessionLocal, engine, Base
from logging_config import logger
from typing import List, Protocol

from playwright.sync_api import sync_playwright

from app2.models import Book
from app2.scrapping_page_url.scrapping_url import book_product_links_generator
from app2.scrapping_product_page.product_page import parce_book

task_queue = queue.Queue(maxsize=100)
db_queue = queue.Queue()




def worker(result, db_queue):
    with sync_playwright() as play:
        logger.info(f"Getting started: {len(result)} links")
        browser = play.chromium.launch(headless=True)
        context = browser.new_context()
        page = browser.new_page()
        for url in result:
            try:
                page.goto(url, timeout=60000)
                book = parce_book(page)
                logger.info(f"Successfully collected {book.title}")
                db_queue.put(book)
            except Exception as e:
                logger.error(f"Error on page: {url}: {e}")
        context.close()
        browser.close()

def db_writer(db_queue):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        while True:
            book_data = db_queue.get()
            if book_data is None:
                break
            try:
                existing_book = session.query(Book).filter(Book.title == book_data.title).first()
                if existing_book:
                    existing_book.price = book_data.price
                    existing_book.description = book_data.description
                    existing_book.stock_availability = book_data.stock_availability
                else:
                    session.add(book_data)
                    session.commit()
                logger.info(f"Entry confirmed: {book_data.title}")
            except Exception as e:
                logger.info(f"Error SQL: {e}")
                session.rollback()
            finally:
                db_queue.task_done()
    except Exception as e:
        logger.error(f"Error on database: {e}")
    finally:
        session.close()



def main(db_queue):
    logger.info("Collected links")
    all_urls = list(book_product_links_generator())
    num_processes = 3
    result = []
    size = (len(all_urls) + num_processes - 1) // num_processes
    for i in range(0, len(all_urls), size):
        slice_list_url = all_urls[i : i + size]
        result.append(slice_list_url)

    processes = []
    for res in result:
        p = multiprocessing.Process(target=worker, args=(res, db_queue))
        p.start()
        processes.append((p, res))

    while True:
        active_processes = [p for p, chunk in processes if p.is_alive()]
        if not active_processes:
            break
        for i, (p, chunk) in enumerate(processes):
            if not p.is_alive() and p.exitcode != 0:
                new_p = multiprocessing.Process(target=worker, args=(chunk,))
                new_p.start()
                processes[i] = (new_p, chunk)
        time.sleep(5)


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    shared_db_queue = manager.Queue()
    writer_process = multiprocessing.Process(target=db_writer, args=(shared_db_queue,))
    writer_process.start()

    try:
        main(shared_db_queue)
    finally:
        shared_db_queue.put(None)
        writer_process.join()
        logger.info("Finish!")

