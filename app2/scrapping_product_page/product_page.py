from app2.models import Book, BookData

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def parce_product_information(browser_page):
    result = {}
    info = browser_page.locator("table.table-striped tr").all()
    for text in info:
        key = text.locator("th").inner_text().strip()
        value = text.locator("td").inner_text().strip()
        result[key] = value
    return result


def parce_book(browser_page) -> BookData:
    rating_class = browser_page.locator(".product_main .star-rating").get_attribute("class") or ""
    rating_word = rating_class.replace("star-rating ", "").strip()
    rating_value = RATING_MAP.get(rating_word, 0)
    try:
        description = browser_page.locator("//div[@id='product_description']/following-sibling::p").inner_text(timeout=3000)
    except:
        description = "No description"
    return Book(
        title=browser_page.locator("h1").inner_text(),
        category=browser_page.locator(".breadcrumb li").nth(2).inner_text().strip(),
        price=float(browser_page.locator(".product_main .price_color").inner_text().replace("£", "")),
        rating=rating_value,
        stock_availability=browser_page.locator(".product_main .instock.availability").inner_text().strip(),
        image_url= browser_page.locator(".item.active img").get_attribute("src").replace("../../", "https://books.toscrape.com/"),
        description=description,
        product_information=parce_product_information(browser_page),
    )
