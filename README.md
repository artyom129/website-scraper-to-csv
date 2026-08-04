# Website Scraper to CSV

A clean Python scraping project that collects structured product data across multiple pages and exports deduplicated records to CSV.

## Business problem

Manual data collection from product catalogs and directories is slow, repetitive, and difficult to keep consistent. This project demonstrates a reusable scraping pipeline that handles page requests, parsing, pagination, deduplication, and structured export.

## Features

- Loads pages with request timeouts and a browser-style User-Agent
- Extracts title, price, availability, rating, and product URL
- Follows pagination links
- Prevents duplicate records by product URL
- Adds a configurable delay between requests
- Exports UTF-8 CSV data
- Keeps parsing, crawling, deduplication, and export logic separated

## Demo source

The included configuration uses `books.toscrape.com`, a website designed specifically for safe scraping practice. The same structure can be adapted to directories, listings, catalogs, and lead-generation sources where collection is permitted.

## Tech stack

Python, Requests, BeautifulSoup, CSV, HTML parsing, web scraping.

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

Install and run:

```bash
pip install -r requirements.txt
python website_scraper_to_csv.py
```

The output will appear at:

```text
output/scraped_books.csv
```

## Output columns

```text
title,price,availability,rating,product_url
```

## Example adaptations

- Business directory extraction
- Real estate listings
- Ecommerce catalog research
- Lead-list preparation
- Product availability tracking
- Structured website-to-CSV workflows

## Portfolio positioning

This is a personal demonstration project built to showcase pagination, structured extraction, duplicate handling, request safety, and CSV automation.
