import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from concurrent.futures import ThreadPoolExecutor
import os
import re

# ---------------- CONFIG ---------------- #

MAX_LINKS = 400
CONCURRENCY = 10

LINK_DIR = "links"
CACHE_DIR = "cache"

os.makedirs(LINK_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------- UTILS ---------------- #

def page_title_from_url(url):
    """
    https://en.wikipedia.org/wiki/Python_(programming_language)
    -> Python (programming language)
    """
    title = url.split("/wiki/")[-1]
    title = unquote(title)
    title = title.replace("_", " ")
    return title


def clean_text(text):
    text = re.sub(r"\[\d+\]", "", text)
    return text.strip()

# ---------------- LINK SCRAPING ---------------- #

def scrape_links(
    url,
    visited,
    dest_url=None
):

    print(f"\nScraping links from: {url}")

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

    except Exception as e:

        print("Request failed:", e)
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    links = set()

    found_destination = False

    for a in soup.select("a[href*='/wiki/']"):

        href = a.get("href")

        if ":" in href:
            continue

        full = urljoin(
            "https://en.wikipedia.org",
            href
        )

        if full in visited:
            continue

        # Always include destination
        if full == dest_url:
            links.add(full)
            found_destination = True
            break

        # Normal link limit
        if len(links) < MAX_LINKS:
            links.add(full)

    title = page_title_from_url(url)

    path = os.path.join(
        LINK_DIR,
        f"{title}.txt"
    )

    with open(path, "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")

    print(f"Saved {len(links)} links → {path}")


    return list(links)


# ---------------- CONTENT FETCH ---------------- #

def scrape_content(url):

    fname = os.path.join(
        CACHE_DIR,
        page_title_from_url(url) + ".txt"
    )

    # Cache hit
    if os.path.exists(fname):
        with open(fname, encoding="utf-8") as f:
            return f.read()

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        lead = None

        for p in soup.find_all("p"):

            text = clean_text(
                p.get_text(" ", strip=True)
            )

            if len(text) > 50:
                lead = text
                break

        if not lead:
            return None

        with open(fname, "w", encoding="utf-8") as f:
            f.write(lead)

        return lead

    except Exception:
        return None


def scrape_contents(urls):

    with ThreadPoolExecutor(
        max_workers=CONCURRENCY
    ) as executor:

        return list(
            executor.map(scrape_content, urls)
        )