# BooksToScrape ETL (Scrape → Excel → MySQL)

A simple end-to-end data pipeline project using https://books.toscrape.com/

## What it does
- Scrapes all book detail pages (title, price, stock, description)
- Exports data to Excel (`booktoscrape.xlsx`)
- Loads data into MySQL using SQLAlchemy + pandas `to_sql`

## Tech stack
- Python, requests, BeautifulSoup
- pandas
- MySQL, SQLAlchemy, PyMySQL
- python-dotenv

## How to run
1.Install dependencies:
```bash
pip install -r requirements.txt

2.Create a .env file (see .env.example):
DB_USER=root
DB_PASS=your_password_here
DB_HOST=host
DB_PORT=port

3.Make sure MySQL database exists
CREATE DATABASE books_bookstoscrape;

4.Run
python Yourpyname.py


Output

Excel saved to Desktop: booktoscrape.xlsx


MySQL table: books_bookstoscrape.books (mode: replace)
