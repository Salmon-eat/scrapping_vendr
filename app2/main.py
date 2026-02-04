import multiprocessing
import queue
import time

from playwright.sync_api import sync_playwright

from app2.scrapping_page_url.scrapping_url import book_product_links_generator
from app2.scrapping_product_page.prosuct_page import parce_book

task_queue = queue.Queue(maxsize=100)
db_queue = queue.Queue()


def worker(result):
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=False)
        page = browser.new_page()
        for url in result:
            try:
                page.goto(url, timeout=30000)
                book = parce_book(page)
                print(f"Воркер: {book.price}")
            except Exception as e:
                print(f"Error - {e}")
        browser.close()


def main():
    all_urls = list(book_product_links_generator())
    num_processes = 3
    result = []
    size = (len(all_urls) + num_processes - 1) // num_processes
    for i in range(0, len(all_urls), size):
        slice_list_url = all_urls[i : i + size]
        result.append(slice_list_url)

    processes = []
    for res in result:
        p = multiprocessing.Process(target=worker, args=(res,))
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
    main()
