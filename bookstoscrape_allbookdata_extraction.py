#/books.toscrape:data collect
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,quote_plus
import os
import json
import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.engine import URL
from sqlalchemy.types import String, Text, Float
from dotenv import load_dotenv



base_url="https://books.toscrape.com/catalogue/page-{}.html"
detail_base="https://books.toscrape.com/catalogue/"


s=requests.Session()
s.headers.update({
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0"
})

#get html from url
def get_html(session,url):
    resp=session.get(url,timeout=20)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding 
    return BeautifulSoup(resp.text,"lxml")

#get links from one pagehtml
def get_links(page_html):
    all_links=page_html.select(".image_container a")
    links=[]
    for el in all_links:
        link=urljoin(detail_base,el.get("href"))
        links.append(link)
    return links


#go through each link to garb data
def data_from_links(all_links):
    book_data=[]
    for ln in all_links:
        link_html=get_html(s,ln)
        title_el=link_html.select_one(".product_main h1")
        book_title=title_el.get_text(strip=True) if title_el else ""
        price_el=link_html.select_one(".price_color")
        book_price=float(price_el.get_text(strip=True).replace("£","")) if price_el else ""
        stock_el=link_html.select_one("p.instock.availability")
        book_stock=stock_el.get_text(strip=True) if stock_el else ""
        des_el=link_html.select_one("#product_description+p")
        book_des=des_el.get_text(strip=True) if des_el else ""
        book_data.append({
            "Title": book_title,
            "Price": book_price,
            "Stock": book_stock,
            "Description": book_des
        })
    return book_data

        
def main():
    all_data=[]
    for p in range(1,51):
        full_url=base_url.format(p)
        page_resp=get_html(s,full_url)
        page_links=get_links(page_resp)
        print(f"links grabbed at this page:{len(page_links)}")
        full_data=data_from_links(page_links)
        all_data.extend(full_data)

    #output as xlsx to desktop
    desktop=os.path.join(os.path.expanduser("~"),"Desktop")
    xlsx_path=os.path.join(desktop,"booktoscrape.xlsx")
    df=pd.DataFrame(all_data)
    df.to_excel(xlsx_path,index=False)
    print("excel saved")
    
    #output data to MYSQL
    pass_path=os.path.join(desktop,".env")
    load_dotenv(pass_path)
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS") 
    DB_HOST = os.getenv("DB_HOST") 
    DB_PORT = int(os.getenv("DB_PORT"))
    DB_NAME = "books_bookstoscrape"

    if not all([DB_USER, DB_PASS, DB_HOST]):
        raise RuntimeError("Missing DB_USER/DB_PASS/DB_HOST in .env")

    engine = create_engine(
        URL.create(
            "mysql+pymysql",
            username=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            query={"charset": "utf8mb4"},
        )
    )  

    with engine.connect() as conn:
        print("✅ connected")
        print("server version:", conn.execute(text("SELECT VERSION()")).scalar())
        print("hostname:", conn.execute(text("SELECT @@hostname")).scalar())
        print("port:", conn.execute(text("SELECT @@port")).scalar())
        print("datadir:", conn.execute(text("SELECT @@datadir")).scalar())
        print("lower_case_table_names:", conn.execute(text("SELECT @@lower_case_table_names")).scalar())

        dbs = conn.execute(text("SHOW DATABASES")).fetchall()
        print("databases:", [r[0] for r in dbs])

        like = conn.execute(text("SHOW DATABASES LIKE 'Books_bookstoscrape'")).fetchall()
        print("LIKE Books_bookstoscrape:", like)
    
    table_name="books"
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",   
        index=False,
        chunksize=200,
        method="multi",
        dtype={                
            "Title": String(500),
            "Price": Float(),
            "Stock": String(200),
            "Description": Text(),
        }

    )
    print(f"✅ saved to MySQL table: {DB_NAME}.{table_name}")


if __name__=="__main__":
    main()

        


        







