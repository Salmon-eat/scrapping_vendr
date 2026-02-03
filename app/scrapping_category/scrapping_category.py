def categories(category_tree):
    return category_tree.xpath("//a[contains(@href, '/it-infrastructure/')]/@href")
