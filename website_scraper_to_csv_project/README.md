# Website Scraper to CSV

A Python web scraping automation project that extracts structured data from a website and saves the results into a clean CSV file.

This portfolio project demonstrates a simple but practical scraping workflow: page loading, HTML parsing, pagination, duplicate removal, and CSV export.

## What this project does

- Scrapes product data from a demo website
- Extracts title, price, availability, rating, and product URL
- Handles pagination
- Removes duplicate records
- Exports clean results to CSV
- Uses a browser-like User-Agent header
- Keeps the code simple and easy to adapt

## Tech Stack

- Python
- requests
- BeautifulSoup
- CSV
- Web scraping
- Data extraction

## How to run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the scraper:

```bash
python website_scraper_to_csv.py
```

3. The output file will appear here:

```text
output/scraped_books.csv
```

## Example output columns

```text
title, price, availability, rating, product_url
```

## Why this project is useful

Businesses often need to collect structured data from websites for research, reporting, lead generation, product tracking, or internal databases. This project shows how a Python scraper can collect website data and export it into a clean CSV file.

## Example use cases

This project can be adapted for product scraping, directory scraping, lead list creation, real estate data collection, ecommerce price monitoring, website data extraction, and CSV export automation.

## Portfolio description

I built a Python web scraper that extracts structured data from multiple website pages, removes duplicates, and exports the results to a clean CSV file. This type of automation helps businesses save time on manual data collection and repetitive copy-paste work.