from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "scraped_books.csv"


@dataclass
class Book:
    title: str
    price: str
    availability: str
    rating: str
    product_url: str


def fetch_page(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_rating(article) -> str:
    rating_element = article.select_one(".star-rating")
    if not rating_element:
        return ""

    classes = rating_element.get("class", [])
    for item in classes:
        if item != "star-rating":
            return item

    return ""


def parse_books_from_page(soup: BeautifulSoup) -> list[Book]:
    books: list[Book] = []

    for article in soup.select("article.product_pod"):
        title_element = article.select_one("h3 a")
        price_element = article.select_one(".price_color")
        availability_element = article.select_one(".availability")
        product_link = title_element.get("href", "") if title_element else ""

        book = Book(
            title=title_element.get("title", "").strip() if title_element else "",
            price=price_element.get_text(strip=True) if price_element else "",
            availability=availability_element.get_text(" ", strip=True) if availability_element else "",
            rating=extract_rating(article),
            product_url=urljoin(BASE_URL, product_link),
        )

        books.append(book)

    return books


def find_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    next_link = soup.select_one("li.next a")
    if not next_link:
        return None

    href = next_link.get("href")
    if not href:
        return None

    return urljoin(current_url, href)


def scrape_books(max_pages: int = 3, delay_seconds: float = 1.0) -> list[Book]:
    all_books: list[Book] = []
    current_url: str | None = BASE_URL
    page_number = 1

    while current_url and page_number <= max_pages:
        print(f"Scraping page {page_number}: {current_url}")

        soup = fetch_page(current_url)
        books = parse_books_from_page(soup)
        all_books.extend(books)

        current_url = find_next_page_url(soup, current_url)
        page_number += 1

        if current_url:
            time.sleep(delay_seconds)

    return remove_duplicates(all_books)


def remove_duplicates(books: Iterable[Book]) -> list[Book]:
    unique: list[Book] = []
    seen_urls: set[str] = set()

    for book in books:
        if book.product_url in seen_urls:
            continue

        seen_urls.add(book.product_url)
        unique.append(book)

    return unique


def export_to_csv(books: list[Book]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "price", "availability", "rating", "product_url"],
        )
        writer.writeheader()

        for book in books:
            writer.writerow({
                "title": book.title,
                "price": book.price,
                "availability": book.availability,
                "rating": book.rating,
                "product_url": book.product_url,
            })


def main() -> None:
    books = scrape_books(max_pages=3)
    export_to_csv(books)

    print(f"Done. Scraped records: {len(books)}")
    print(f"CSV file created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
