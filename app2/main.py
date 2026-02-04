import queue
import multiprocessing
from playwright.sync_api import sync_playwright

from app2.scrapping_page_url.scrapping_url import book_product_links_generator
from app2.scrapping_product_page.prosuct_page import product_page

task_queue = queue.Queue(maxsize=100)
db_queue = queue.Queue()


def worker(result):
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=False)
        page = browser.new_page()
        for url in result:
            page.goto(url)
            print(product_page())
            return product_page()
        browser.close()

def main(all_urls):
    num_processes = 3
    result = []
    size = (len(all_urls) + num_processes - 1) // num_processes
    for i in range(0, len(all_urls), size):
        slice_list_url = all_urls[i:i + size]
        result.append(slice_list_url)

    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(worker, result)


if __name__ == "__main__":
    all_urls = list(book_product_links_generator())
    main(all_urls)