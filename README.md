# Website Scraper to CSV

[![Tests](https://github.com/artyom129/website-scraper-to-csv/actions/workflows/tests.yml/badge.svg)](https://github.com/artyom129/website-scraper-to-csv/actions/workflows/tests.yml)

Languages: English · [Русский](README.ru.md) · [Қазақша](README.kk.md)

A Python scraper that walks through a paginated product catalog, collects the products on every page, drops duplicates, and saves the result as a CSV file. The demo targets [books.toscrape.com](https://books.toscrape.com/), a site built for scraping practice.

## What problem it solves

Copying product data out of catalogs and directories by hand is slow, and the result is rarely consistent. This script does the same job in one command and produces the same columns every time, ready to open in Excel or import elsewhere.

## What it does

- Starts from any listing page and follows the "next" link until the pages run out or a page limit is reached.
- Reads the title, price, availability, rating, and product URL of every item.
- Resolves product links against the page they appeared on. On this catalog, page 2 and later use different relative paths than page 1, and the script handles that.
- Keeps one record per product URL.
- Retries timeouts, connection errors, and 5xx responses with a growing pause. A 404 is not retried.
- Stops if the pagination links form a loop.
- Waits between requests so it does not hammer the server (one second by default).
- Writes UTF-8 with a byte order mark, so Excel shows the `£` sign correctly.

## Quick start

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install the dependencies and run:

```bash
pip install -r requirements.txt
python website_scraper_to_csv.py
```

By default it scrapes three pages and writes `output/scraped_books.csv`.

## Usage

```bash
python website_scraper_to_csv.py                       # 3 pages, default file
python website_scraper_to_csv.py --max-pages 0         # every page
python website_scraper_to_csv.py --delay 2 -o books.csv
python website_scraper_to_csv.py --url https://books.toscrape.com/catalogue/page-5.html
python website_scraper_to_csv.py --help
```

| Option | Description | Default |
|---|---|---|
| `--url` | Page to start from | `https://books.toscrape.com/` |
| `--max-pages` | Number of pages to scrape, `0` for no limit | `3` |
| `--delay` | Seconds to wait between requests | `1` |
| `-o`, `--output` | CSV file to create | `output/scraped_books.csv` |

The exit code is `0` on success and `1` if a page cannot be downloaded, so the script can run in a scheduled job.

Output for two pages:

```text
Scraping page 1: https://books.toscrape.com/
Scraping page 2: https://books.toscrape.com/catalogue/page-2.html
Done. Scraped records: 40
CSV file created: output/scraped_books.csv
```

## Output columns

```text
title,price,availability,rating,product_url
```

## Adapting it to another site

The parsing lives in `parse_books_from_page` and uses CSS selectors (`article.product_pod`, `.price_color`, and so on). To scrape a different catalog, change those selectors and the `Book` fields. The pagination, retry, deduplication, and export code does not depend on the site. Check the site's terms and robots.txt before you scrape it.

Typical uses: business directories, real estate listings, e-commerce catalog research, and product availability tracking.

## Tests

```bash
python -m pytest -q
```

The tests run without a network. They cover parsing, link resolution on later pages, pagination and the page limit, loop protection, deduplication, retries, charset handling, the CSV file, and the command line.

## Project layout

```text
.
├── website_scraper_to_csv.py     # fetching, parsing, crawling, export, CLI
├── tests/test_scraper.py
├── requirements.txt
└── .github/workflows/tests.yml   # CI on Python 3.11 and 3.12
```

## About

A personal demonstration project for pagination, structured extraction, duplicate handling, and CSV automation.
