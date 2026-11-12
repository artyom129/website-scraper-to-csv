"""Scrape a paginated product catalog into a deduplicated CSV file.

Usage:
    python website_scraper_to_csv.py [--url URL] [--max-pages N] [-o FILE]
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
OUTPUT_FILE = Path(__file__).resolve().parent / "output" / "scraped_books.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


@dataclass
class Book:
    title: str
    price: str
    availability: str
    rating: str
    product_url: str


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def fetch_page(
    url: str,
    timeout_seconds: float = 20,
    retries: int = 2,
    backoff_seconds: float = 1.0,
) -> BeautifulSoup:
    """Download a page. Retries connection errors, timeouts and 5xx responses."""
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout_seconds)
            response.raise_for_status()
            # Parse the raw bytes so BeautifulSoup reads the charset from the
            # page itself. response.text guesses ISO-8859-1 when the server
            # sends no charset, which turns "£" into "Â£".
            return BeautifulSoup(response.content, "html.parser")
        except requests.HTTPError as error:
            last_error = error
            status = error.response.status_code if error.response is not None else 500
            if status < 500:  # a client error will not fix itself
                break
        except requests.RequestException as error:
            last_error = error

        if attempt < retries:
            time.sleep(backoff_seconds * (2 ** attempt))

    raise last_error if last_error else RuntimeError(f"Could not fetch {url}")


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def extract_rating(article) -> str:
    rating_element = article.select_one(".star-rating")
    if not rating_element:
        return ""

    for item in rating_element.get("class", []):
        if item != "star-rating":
            return item

    return ""


def parse_books_from_page(soup: BeautifulSoup, page_url: str = BASE_URL) -> list[Book]:
    """Parse one listing page. Links are resolved against ``page_url``."""
    books: list[Book] = []

    for article in soup.select("article.product_pod"):
        title_element = article.select_one("h3 a")
        price_element = article.select_one(".price_color")
        availability_element = article.select_one(".availability")
        product_link = title_element.get("href", "") if title_element else ""

        books.append(Book(
            title=title_element.get("title", "").strip() if title_element else "",
            price=price_element.get_text(strip=True) if price_element else "",
            availability=(availability_element.get_text(" ", strip=True)
                          if availability_element else ""),
            rating=extract_rating(article),
            # Relative links must be resolved against the page they came from:
            # on page 2 and later the catalog uses paths relative to /catalogue/.
            product_url=urljoin(page_url, product_link) if product_link else "",
        ))

    return books


def find_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    next_link = soup.select_one("li.next a")
    if not next_link:
        return None

    href = next_link.get("href")
    if not href:
        return None

    return urljoin(current_url, href)


# --------------------------------------------------------------------------
# Crawling and cleaning
# --------------------------------------------------------------------------

def scrape_books(
    start_url: str = BASE_URL,
    max_pages: int = 3,
    delay_seconds: float = 1.0,
    verbose: bool = True,
) -> list[Book]:
    """Follow pagination from ``start_url``. ``max_pages <= 0`` means no limit."""
    all_books: list[Book] = []
    visited: set[str] = set()
    current_url: str | None = start_url
    page_number = 1

    while current_url and current_url not in visited:
        if max_pages > 0 and page_number > max_pages:
            break

        if verbose:
            print(f"Scraping page {page_number}: {current_url}")

        visited.add(current_url)
        soup = fetch_page(current_url)
        all_books.extend(parse_books_from_page(soup, current_url))

        current_url = find_next_page_url(soup, current_url)
        page_number += 1

        if current_url and delay_seconds > 0:
            time.sleep(delay_seconds)

    return remove_duplicates(all_books)


def remove_duplicates(books: Iterable[Book]) -> list[Book]:
    """Keep the first book for every product URL. Books without a URL are dropped."""
    unique: list[Book] = []
    seen_urls: set[str] = set()

    for book in books:
        if not book.product_url or book.product_url in seen_urls:
            continue

        seen_urls.add(book.product_url)
        unique.append(book)

    return unique


# --------------------------------------------------------------------------
# Export and CLI
# --------------------------------------------------------------------------

def export_to_csv(books: list[Book], output_file: Path = OUTPUT_FILE) -> Path:
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # UTF-8 with a BOM, so Excel shows "£" correctly when the file is opened.
    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=[f.name for f in fields(Book)])
        writer.writeheader()
        writer.writerows(asdict(book) for book in books)

    return output_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape a paginated product catalog into a CSV file.")
    parser.add_argument("--url", default=BASE_URL,
                        help=f"first page to scrape (default: {BASE_URL})")
    parser.add_argument("--max-pages", type=int, default=3,
                        help="how many pages to scrape, 0 for all (default: 3)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="seconds to wait between requests (default: 1)")
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_FILE,
                        help="CSV file to create (default: output/scraped_books.csv)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        books = scrape_books(args.url, args.max_pages, args.delay)
    except requests.RequestException as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    path = export_to_csv(books, args.output)
    print(f"Done. Scraped records: {len(books)}")
    print(f"CSV file created: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
