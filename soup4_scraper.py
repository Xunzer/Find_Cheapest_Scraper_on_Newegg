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

# create a new .csv file to write in the data
filename = "findcheapest.csv"
f = open(filename, "w", encoding="utf-8")

# first writing in the headers
headers = "product_name, product_price, product_link\n" # .csv are delimited by newlines
f.write(headers)

possible_choice = {} # intiailize the dictionary to store the price and its name

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
        price_tag = i_grand_parent.find(class_="price-current").strong # find the "price-current" which contains the price number and specify the tag name
        if price_tag == None: # if there are some special deals, we might not be able to retrieve the tag from the html but get a None object instead
            continue
        price = price_tag.string # retrieve the value from tag

        possible_choice[item.replace(",", "")] = {"price": int(price.replace(",", "")), "link": link} # store the key-value pair inside the dictionary. Remove the commas from the price by calling replace() and convert it to an int
        print(possible_choice)

sorted_choice = sorted(possible_choice.items(), key=lambda x: x[1]["price"]) # we pass a lambda function into the sorted as the key, which is an anonymous function that takes a tuple and returns the value associated with the key "price" in the value dictionary, then the sorted() would sort the list of tuples based on the "price" values

# for loop to process each eligible item in sorted dictionary
for item in sorted_choice:
    product_name = item[0]
    product_price = f"${item[1]["price"]}"
    product_link = item[1]["link"]

    # print in terminal
    print(product_name)
    print(product_price)
    print(product_link)
    print("----------------------------------------------------------------------------------")

    f.write(product_name + "," + product_price + "," + product_link + "\n") # write the data into the .csv file, already converted all in-text commas to None so that it wouldn't be treated as new columns

# close the .csv file
f.close()