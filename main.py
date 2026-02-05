import multiprocessing
from typing import Any, List

from playwright.sync_api import Page, sync_playwright

from app2.db import Base, SessionLocal, engine
from app2.models import Book
from app2.scrapping_page_url.scrapping_url import book_product_links_generator
from app2.scrapping_product_page.product_page import parse_book
from logging_config import logger


class ScraperWorker:
    def __init__(self, db_queue: multiprocessing.Queue):
        self.db_queue = db_queue

    def runner(self, urls: List[str]) -> None:
        with sync_playwright() as play:
            browser = play.chromium.launch(headless=True)
            context = browser.new_context()
            page = browser.new_page()
            for url in urls:
                self._process_url(page, url)
            context.close()
            browser.close()

    def _process_url(self, page: Page, url: str) -> None:
        try:
            page.goto(url, timeout=60000)
            book = parse_book(page)
            self.db_queue.put(book)
        except Exception as e:
            logger.error(f"Error on page: {url}: {e}")


class PostgresBookWriter:
    def __init__(self) -> None:
        Base.metadata.create_all(bind=engine)

    def write(self, book_data: Book) -> None:
        session = SessionLocal()
        try:
            session.merge(book_data)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error SQL: {e}")
        finally:
            session.close()


def db_writer_process(db_queue: Any) -> None:
    try:
        writer = PostgresBookWriter()
        while True:
            book = db_queue.get()
            if book is None:
                break
            writer.write(book)
            db_queue.task_done()
    except Exception:
        logger.error(f"Error proces in database")


class ScraperDivisionWork:
    def __init__(self, num_workers: int = 3):
        self.num_workers = num_workers
        self.manager = multiprocessing.Manager()
        self.db_queue = self.manager.Queue(maxsize=100)

    def _split_urls(self, urls: List[str]) -> List[List[str]]:
        result = []
        total_urls = len(urls)

        if total_urls == 0:
            return result

        size = (total_urls + self.num_workers - 1) // self.num_workers

        for i in range(0, total_urls, size):
            slice_list_url = urls[i : i + size]
            result.append(slice_list_url)

        return result

    def start(self) -> None:
        logger.info("Starting")
        urls = list(book_product_links_generator())
        chunks = self._split_urls(urls)

        writer_p = multiprocessing.Process(
            target=db_writer_process, args=(self.db_queue,)
        )
        writer_p.start()

        workers = []
        for chunk in chunks:
            worker_instance = ScraperWorker(self.db_queue)
            p = multiprocessing.Process(target=worker_instance.runner, args=(chunk,))
            p.start()
            workers.append(p)

        for p in workers:
            p.join()

        self.db_queue.put(None)
        writer_p.join()
        logger.info("Finished")


if __name__ == "__main__":
    orchestrator = ScraperDivisionWork(num_workers=3)
    orchestrator.start()
