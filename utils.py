
def get_max_pages(num_items, items_per_page):
    if num_items < items_per_page:
        return 1
    elif num_items % items_per_page == 0:
        return num_items // items_per_page
    else:
        return num_items // items_per_page + 1
