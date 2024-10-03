import requests
from bs4 import BeautifulSoup

def download_anime(anime_title, url):
    r = requests.get(url, stream=True)
    with open(f'{anime_title}.mp4', 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


if __name__ == "__main__":
    print("Welcome to the Hianime Downloader")
    print("This program allows you to download anime from hianime.to")
    anime_title = input("Enter the name of the anime you want to download (Optional): ")
    url = input("Enter the URL of the anime you want to download: ")
    download_anime(anime_title, url)
