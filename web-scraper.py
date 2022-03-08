#web scraper to pull data and files from websites using python

import requests
url = input("Enter URL: ")

r = requests.get(url)
with open("test.txt", 'wb') as f:
    f.write(r.content)
