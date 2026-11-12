# Upwork Portfolio Entry

## Title

Multi-Page Website Scraper with CSV Export

## Description

Built a Python web scraper that walks through a paginated product catalog, collects structured product data from every page, removes duplicate records, and exports a clean CSV file.

The scraper resolves product links against the page they came from, retries temporary server errors with a growing pause, stops on pagination loops, and runs from the command line with a proper exit code. Fetching, parsing, crawling, deduplication, and export are separate functions, so the same code can be pointed at another directory, listing site, or catalog where scraping is allowed. 18 automated tests run without a network.

## Technologies

Python, Requests, BeautifulSoup, CSV, HTML parsing, web scraping, pytest, GitHub Actions.

## Client value

The script replaces repetitive manual data collection and produces structured records ready for spreadsheets, research, reporting, or CRM import.
