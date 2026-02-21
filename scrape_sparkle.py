import requests
from bs4 import BeautifulSoup
import json
import re
import time

BASE = "https://sparklecannabis.ca/menu/burlington/categories/"

CATEGORIES = [
    "dried-flower/",
    "vapes/",
    "pre-rolls/",
    "edibles/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-CA,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive"
}


def get_product_links(category_url):
    res = requests.get(category_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        if "/products/" in a["href"]:
            links.add(a["href"])

    return list(links)

def scrape_product(url):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text()

    # More reliable product name extraction
    meta_title = soup.find("meta", property="og:title")
    name = meta_title["content"].strip() if meta_title else None

    # Clean name (remove site name if present)
    if name and " - Sparkle Cannabis" in name:
        name = name.split(" - ")[0]

    price_match = re.search(r"\$[0-9]+\.[0-9]{2}", text)
    thc_match = re.search(r"THC:\s*[0-9.\- ]+%", text)
    cbd_match = re.search(r"CBD:\s*[0-9.\- ]+%", text)

    return {
    "name": name,
    "price": price_match.group() if price_match else None,
    "thc": thc_match.group() if thc_match else None,
    "cbd": cbd_match.group() if cbd_match else None,
    "in_stock": in_stock,
    "url": url
}



all_products = []

for cat in CATEGORIES:
    category_url = BASE + cat
    print(f"Scraping category: {category_url}")

    links = get_product_links(category_url)

    for link in links:
        if link.startswith("/"):
            link = "https://sparklecannabis.ca" + link

        try:
            product = scrape_product(link)
            all_products.append(product)
            print("Scraped:", product["name"])
            time.sleep(0.5)
        except Exception as e:
            print("Error:", link, e)

with open("menu.json", "w") as f:
    json.dump(all_products, f, indent=2)

print("Done. Saved to menu.json")
