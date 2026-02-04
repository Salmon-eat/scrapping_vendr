from app2.scrapping_page_url.scrapping_url import book_product_links_generator



if __name__ == "__main__":
    generator = book_product_links_generator()
    for g in generator:
        print(g)
