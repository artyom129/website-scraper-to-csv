<a id="english"></a>

<div align="center">

**🇬🇧 English** · [🇷🇺 Русский](#russian)

</div>

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

---

<a id="russian"></a>

<div align="center">

[🇬🇧 English](#english) · **🇷🇺 Русский**

</div>

# Website Scraper to CSV — Русская версия

Python-скрапер для сбора структурированных данных с нескольких страниц сайта и экспорта результата в CSV без дублей.

## Что решает проект

Ручной сбор данных из каталогов, листингов и директорий занимает много времени и легко приводит к ошибкам. Этот проект показывает повторно используемый пайплайн: загрузка страниц, парсинг, пагинация, дедупликация и экспорт.

## Возможности

- HTTP-запросы с timeout и User-Agent;
- извлечение названия, цены, наличия, рейтинга и URL товара;
- переход по страницам пагинации;
- удаление дублей по URL товара;
- настраиваемая задержка между запросами;
- экспорт UTF-8 CSV;
- разделение логики загрузки, парсинга, обхода страниц и экспорта.

## Демонстрационный источник

В конфигурации используется `books.toscrape.com` — сайт, созданный специально для безопасной практики веб-скрапинга.

## Стек

Python, Requests, BeautifulSoup, CSV, HTML parsing, web scraping.

## Запуск

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
python website_scraper_to_csv.py
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python website_scraper_to_csv.py
```

Результат:

```text
output/scraped_books.csv
```

## Где можно адаптировать

- бизнес-каталоги;
- объявления недвижимости;
- исследование ecommerce-каталогов;
- подготовка лид-листов;
- мониторинг доступности товаров;
- автоматизация сайт → CSV.

Проект демонстрирует пагинацию, структурированный парсинг, дедупликацию и автоматический экспорт данных.
