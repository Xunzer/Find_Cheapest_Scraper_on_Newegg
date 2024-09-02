from bs4 import BeautifulSoup as soup
import requests
import re

# base url for new egg
base_url = "https://www.newegg.ca/p/pl"

# name of the product
search = input("What product do you want to search for? ")

# keep the query parameter "N" to show in-stock items only
my_url = f"{base_url}?d={search}&N=4131"

# access the attribute of the Response object to convert the response content to a string and store it in the page_html variable
page_html = requests.get(my_url).text

# parse the string as html and store it
page_parsed = soup(page_html, "html.parser")

# <span class="list-tool-pagination-text">Page<!-- --> <strong>1<!-- -->/<!-- -->2</strong></span>
# get the parent of max page number element and convert it to a string, then use split() twice on it and get everything remaining in the last item (so that the last "<" is removed)
page_num_text = page_parsed.find(class_="list-tool-pagination-text").strong
max_page = int(str(page_num_text).split("/")[1].split(">")[1][:-1])

# Get the content for every single page available. The first page is page 1, so increment both start and end of range. Search for the titles in the file to narrow down the scope
for page in range(1, max_page + 1):
    page_url = f"{base_url}?d={search}&N=4131&page={page}"
    single_page_html = requests.get(page_url).text
    single_page_parsed = soup(single_page_html, "html.parser")
    title_div = single_page_parsed.find(class_="item-cells-wrap border-cells short-video-box items-list-view is-list")

    # search for everything that contains the key term (e.g. apple and apple juice both would match)
    items = title_div.find_all(text=re.compile(search))

    for item in items:
        i_parent = item.parent # get the parent of the item
        link = None  # guard for error handling
        if i_parent.name != "a": # if the parent tag is not "a", we will skip it to prevent error
            continue
        link = i_parent["href"]

        i_grand_parent = item.find_parent(class_="item-container") # find the "item-container" tag which is the parent of "item-title" tag. find_parent will find the first matching parent in the tree
        price = i_grand_parent.find(class_="price-current").strong.string # find the "price-current" which contains the price number and specify the tag name and access the value

        print(price)