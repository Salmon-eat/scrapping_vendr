from app2.model import Book

ADD_BASE_URL = "https://books.toscrape.com/"


def parce_title(browser_page):
    return browser_page.locator("h1").inner_text()


def parce_category(browser_page):
    return browser_page.locator(".breadcrumb li").nth(2).inner_text().strip()


def parce_price(browser_page):
    text = browser_page.locator(".product_main .price_color").inner_text()
    return float(text.replace("£", ""))


convert = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parce_rating(browser_page):
    rating_element = browser_page.locator(".product_main .star-rating").get_attribute(
        "class"
    )
    rating_word = rating_element.replace("star-rating ", "")
    return convert.get(rating_word, 0)


def parce_stock_availability(browser_page):
    return (
        browser_page.locator(".product_main .instock.availability").inner_text().strip()
    )


def parce_image_url(browser_page):
    url = browser_page.locator(".item.active img").get_attribute("src")
    return f"{ADD_BASE_URL}{url[6:]}"


def parce_description(browser_page):
    return browser_page.locator(
        "//div[@id='product_description']/following-sibling::p"
    ).inner_text()


def parce_product_information(browser_page):
    result = {}
    info = browser_page.locator("table.table-striped tr").all()
    for text in info:
        key = text.locator("th").inner_text().strip()
        value = text.locator("td").inner_text().strip()
        result[key] = value
    return result


def parce_book(browser_page) -> Book:
    return Book(
        title=parce_title(browser_page),
        category=parce_category(browser_page),
        price=parce_price(browser_page),
        rating=parce_rating(browser_page),
        stock_availability=parce_stock_availability(browser_page),
        image_url=parce_image_url(browser_page),
        description=parce_description(browser_page),
        product_information=parce_product_information(browser_page),
    )
