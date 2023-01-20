"""
This module handle the storing while scraping.
"""
import os
from time import sleep

from pymongo import MongoClient

import scraping


def create_mongo_db():
    """This function create a mongoDB database"""
    client = MongoClient('localhost', 27017)
    user_name = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    client.testdb.add_user(str(user_name), str(password), roles=[{'role': 'readWrite', 'db': 'testdb'}])
    database = client['good_reads']
    database.drop_collection("book_info")
    database.drop_collection("author_info")
    database.create_collection("book_info")
    database.create_collection("author_info")
    return database


def scrape_and_store(database, start_url, book_num, author_num):
    """This function store data into database while scraping"""
    book_mongodb = database.get_collection("book_info")
    author_mongodb = database.get_collection("author_info")
    url = start_url
    new_scraper = scraping.Scraper()
    for i in range(book_num):
        scraping.print_scrape_log("Book", str(i + 1))
        book = new_scraper.scraping_book(url)
        new_scraper.scraping_similar_book(book)
        scraping.print_info_log(book)
        book_mongodb.insert_one(book)
        if new_scraper.auth_counter <= author_num:
            author = new_scraper.scraping_author(book)
            if author is not None:
                scraping.print_scrape_log("Author", str(new_scraper.auth_counter))
                new_scraper.scraping_related_author(author)
                scraping.print_info_log(author)
                author_mongodb.insert_one(author)
        sleep(5)
        url = book["similar_books"][0]