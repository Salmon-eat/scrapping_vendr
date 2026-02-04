from playwright.sync_api import sync_playwright

from app2.model import Book

test_url = ["https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"]
ADD_BASE_URL = "https://books.toscrape.com/"

def parce_title(browser_page):
    return browser_page.locator("h1").inner_text()

def parce_category(browser_page):
    pass


def parce_price(browser_page):
    text = browser_page.locator(".product_main .price_color").inner_text()
    return float(text.replace("£", ""))


def parce_rating(browser_page):
    pass


def parce_stock_availability(browser_page):
    pass


def parce_image_url(browser_page):
    url = browser_page.locator(".item.active img").get_attribute("src")
    return  f"{ADD_BASE_URL}{url[6:]}"


def parce_description(browser_page):
    return browser_page.locator("//div[@id='product_description']/following-sibling::p").inner_text()

def parce_product_information(browser_page):
    pass



def product_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_page = browser.new_page()
        try:
            for url in test_url:
                browser_page.goto(url, timeout=15000)
                parce = parce_book(browser_page)
                print(parce)
                yield parce
        except Exception as e:
            print(f"Помилка парсингу: {type(e).__name__} - {e}")
        finally:
            browser.close()

def parce_book(browser_page) -> Book:
    return Book(
        title = parce_title(browser_page),
        # category = parce_category(browser_page),
        price = parce_price(browser_page),
        # rating = parce_rating(browser_page),
        # stock_availability = parce_stock_availability(browser_page),
        image_url = parce_image_url(browser_page),
        description = parce_description(browser_page),
        # product_information = parce_product_information(browser_page),
    )

if __name__ == "__main__":
    for item in product_page():
        pass