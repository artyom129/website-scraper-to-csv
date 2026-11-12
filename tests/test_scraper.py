import csv
from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup

import website_scraper_to_csv as scraper
from website_scraper_to_csv import (
    Book,
    export_to_csv,
    fetch_page,
    find_next_page_url,
    main,
    parse_books_from_page,
    remove_duplicates,
    scrape_books,
)


def listing_html(items, next_href=None):
    """Build a catalog page. ``items`` is a list of (title, relative_href)."""
    articles = "".join(
        f"""
        <article class="product_pod">
          <p class="star-rating Four"></p>
          <h3><a href="{href}" title="{title}">{title[:10]}</a></h3>
          <p class="price_color">£10.00</p>
          <p class="availability">
            In stock
          </p>
        </article>"""
        for title, href in items
    )
    nxt = f'<li class="next"><a href="{next_href}">next</a></li>' if next_href else ""
    return f"<html><body>{articles}<ul>{nxt}</ul></body></html>"


def soup(html):
    return BeautifulSoup(html, "html.parser")


class FakeResponse:
    def __init__(self, content=b"<html></html>", status=200):
        self.content = content
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error", response=self)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(scraper.time, "sleep", lambda _seconds: None)


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def test_parse_books_from_page():
    html = """
    <article class="product_pod">
      <p class="star-rating Three"></p>
      <h3><a href="catalogue/example_1/index.html" title="Example Book">Example</a></h3>
      <p class="price_color">£19.99</p>
      <p class="availability">In stock</p>
    </article>
    """
    books = parse_books_from_page(BeautifulSoup(html, "html.parser"))

    assert len(books) == 1
    assert books[0].title == "Example Book"
    assert books[0].price == "£19.99"
    assert books[0].availability == "In stock"
    assert books[0].rating == "Three"
    assert books[0].product_url.endswith("catalogue/example_1/index.html")


def test_availability_whitespace_is_collapsed():
    books = parse_books_from_page(soup(listing_html([("Book", "book/index.html")])))

    assert books[0].availability == "In stock"


def test_links_are_resolved_against_the_page_they_came_from():
    page = soup(listing_html([("Second", "second_2/index.html")]))
    books = parse_books_from_page(page, "https://shop.test/catalogue/page-2.html")

    assert books[0].product_url == "https://shop.test/catalogue/second_2/index.html"


def test_missing_fields_become_empty_strings():
    page = soup('<article class="product_pod"><h3><a href="x/index.html"></a></h3></article>')
    book = parse_books_from_page(page, "https://shop.test/")[0]

    assert (book.title, book.price, book.availability, book.rating) == ("", "", "", "")
    assert book.product_url == "https://shop.test/x/index.html"


def test_find_next_page_url():
    page = soup(listing_html([], next_href="page-2.html"))

    assert find_next_page_url(page, "https://shop.test/") == "https://shop.test/page-2.html"
    assert find_next_page_url(soup(listing_html([])), "https://shop.test/") is None


# --------------------------------------------------------------------------
# Deduplication
# --------------------------------------------------------------------------

def test_remove_duplicates_by_product_url():
    first = Book("A", "1", "In stock", "Five", "https://example.com/a")
    duplicate = Book("A copy", "2", "In stock", "Four", "https://example.com/a")
    second = Book("B", "3", "In stock", "Three", "https://example.com/b")

    result = remove_duplicates([first, duplicate, second])

    assert result == [first, second]


def test_books_without_a_url_are_dropped():
    assert remove_duplicates([Book("A", "1", "", "", "")]) == []


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def test_fetch_page_reads_the_charset_from_the_page(monkeypatch):
    html = '<meta charset="utf-8"><p class="price_color">£5.00</p>'.encode("utf-8")
    monkeypatch.setattr(scraper.requests, "get", lambda *_a, **_k: FakeResponse(html))

    assert fetch_page("https://shop.test/").select_one(".price_color").text == "£5.00"


def test_server_errors_are_retried(monkeypatch):
    calls = []

    def flaky(*_args, **_kwargs):
        calls.append(1)
        return FakeResponse(status=503) if len(calls) < 3 else FakeResponse()

    monkeypatch.setattr(scraper.requests, "get", flaky)
    fetch_page("https://shop.test/", retries=2)

    assert len(calls) == 3


def test_client_errors_are_not_retried(monkeypatch):
    calls = []

    def not_found(*_args, **_kwargs):
        calls.append(1)
        return FakeResponse(status=404)

    monkeypatch.setattr(scraper.requests, "get", not_found)

    with pytest.raises(requests.HTTPError):
        fetch_page("https://shop.test/", retries=3)
    assert len(calls) == 1


def test_connection_errors_raise_after_all_retries(monkeypatch):
    calls = []

    def down(*_args, **_kwargs):
        calls.append(1)
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(scraper.requests, "get", down)

    with pytest.raises(requests.ConnectionError):
        fetch_page("https://shop.test/", retries=2)
    assert len(calls) == 3


# --------------------------------------------------------------------------
# Crawling
# --------------------------------------------------------------------------

def fake_site(monkeypatch, pages):
    """Serve ``pages`` (url -> html) instead of the network."""
    requested = []

    def fake_fetch(url, *_args, **_kwargs):
        requested.append(url)
        return soup(pages[url])

    monkeypatch.setattr(scraper, "fetch_page", fake_fetch)
    return requested


def three_page_site():
    return {
        "https://shop.test/": listing_html(
            [("One", "catalogue/one_1/index.html")], next_href="catalogue/page-2.html"),
        "https://shop.test/catalogue/page-2.html": listing_html(
            [("Two", "two_2/index.html")], next_href="page-3.html"),
        "https://shop.test/catalogue/page-3.html": listing_html(
            [("Three", "three_3/index.html")]),
    }


def test_scrape_follows_pagination_with_correct_urls(monkeypatch):
    fake_site(monkeypatch, three_page_site())
    books = scrape_books("https://shop.test/", max_pages=0, delay_seconds=0, verbose=False)

    assert [b.title for b in books] == ["One", "Two", "Three"]
    assert [b.product_url for b in books] == [
        "https://shop.test/catalogue/one_1/index.html",
        "https://shop.test/catalogue/two_2/index.html",
        "https://shop.test/catalogue/three_3/index.html",
    ]


def test_max_pages_limits_the_crawl(monkeypatch):
    requested = fake_site(monkeypatch, three_page_site())
    books = scrape_books("https://shop.test/", max_pages=2, delay_seconds=0, verbose=False)

    assert len(books) == 2
    assert len(requested) == 2


def test_pagination_loop_does_not_run_forever(monkeypatch):
    looping = {"https://shop.test/": listing_html(
        [("One", "one_1/index.html")], next_href="https://shop.test/")}
    requested = fake_site(monkeypatch, looping)
    books = scrape_books("https://shop.test/", max_pages=0, delay_seconds=0, verbose=False)

    assert len(books) == 1
    assert requested == ["https://shop.test/"]


def test_overlapping_pages_do_not_create_duplicates(monkeypatch):
    pages = {
        "https://shop.test/": listing_html(
            [("One", "one_1/index.html")], next_href="page-2.html"),
        "https://shop.test/page-2.html": listing_html([("One again", "one_1/index.html")]),
    }
    fake_site(monkeypatch, pages)
    books = scrape_books("https://shop.test/", max_pages=0, delay_seconds=0, verbose=False)

    assert [b.title for b in books] == ["One"]


# --------------------------------------------------------------------------
# Export and CLI
# --------------------------------------------------------------------------

def test_csv_export_round_trip(tmp_path: Path):
    books = [Book('Title, with "quotes"', "£1.00", "In stock", "Two", "https://shop.test/a")]
    path = export_to_csv(books, tmp_path / "nested" / "books.csv")

    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert rows == [{
        "title": 'Title, with "quotes"',
        "price": "£1.00",
        "availability": "In stock",
        "rating": "Two",
        "product_url": "https://shop.test/a",
    }]


def test_cli_success(tmp_path: Path, monkeypatch, capsys):
    fake_site(monkeypatch, three_page_site())
    out = tmp_path / "books.csv"

    code = main(["--url", "https://shop.test/", "--max-pages", "0",
                 "--delay", "0", "-o", str(out)])

    assert code == 0
    assert "Scraped records: 3" in capsys.readouterr().out
    assert out.exists()


def test_cli_returns_1_when_the_site_is_unreachable(tmp_path: Path, monkeypatch, capsys):
    def down(*_args, **_kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(scraper.requests, "get", down)
    out = tmp_path / "books.csv"

    code = main(["--delay", "0", "-o", str(out)])

    assert code == 1
    assert "Error:" in capsys.readouterr().err
    assert not out.exists()
