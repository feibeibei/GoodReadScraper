"""
This module the test of scraping.
"""
import json
import unittest

from pymongo import MongoClient

import interface
import scraping
import network
import storing


def scrape_first_book():
    """This function scrape an example book"""
    start_url = "https://www.goodreads.com/book/show/40597810-daisy-jones-the-six"
    new_scraper = scraping.Scraper()
    book = new_scraper.scraping_book(start_url)
    new_scraper.scraping_similar_book(book)
    return book


def is_json(js_file):
    """This function check whether a file is a json file"""
    f = open(js_file, "r")
    try:
        json.loads(f.read())
    except ValueError:
        return False
    return True


def scrape_first_author():
    """This function scrape an example author"""
    new_scraper = scraping.Scraper()
    book = scrape_first_book()
    author = new_scraper.scraping_author(book)
    new_scraper.scraping_related_author(author)
    return author


def scrape_to_db(book_num, author_num):
    """This function scrape and store data into database"""
    start_url = "https://www.goodreads.com/book/show/40597810-daisy-jones-the-six"
    storing.scrape_and_store(storing.create_mongo_db(), start_url, book_num, author_num)
    client = MongoClient('localhost', 27017)
    database = client['sample_db']
    return database


class TestScraping(unittest.TestCase):
    def test_book_info(self):
        """This function test the correctness of scraped book information"""
        # the book for test is Daisy Jones & the Six
        book = scrape_first_book()
        self.assertEqual(book["_id"], 40597810)
        self.assertEqual(book["book_url"], "https://www.goodreads.com/book/show/40597810-daisy-jones-the-six")
        self.assertEqual(book["book_title"], "Daisy Jones & The Six")
        self.assertEqual(book["ISBN"], "9781524798628")
        self.assertEqual(book["author_url"], "https://www.goodreads.com/author/show/6572605.Taylor_Jenkins_Reid")
        self.assertEqual(book["author_name"], "Taylor Jenkins Reid")
        self.assertEqual(book["image_url"],
                         "https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1580255154i/40597810."
                         "_SR1200,630_.jpg")

    def test_author_info(self):
        """This function test the correctness of scraped author information"""
        # the author for test is the author of Daisy Jones & the Six: Taylor Jenkins Reid
        author = scrape_first_author()
        self.assertEqual(author["_id"], 6572605)
        self.assertEqual(author["author_name"], "Taylor Jenkins Reid")
        self.assertEqual(author["author_url"], "https://www.goodreads.com/author/show/6572605.Taylor_Jenkins_Reid")
        self.assertEqual(author["image_url"], "https://images.gr-assets.com/authors/1493925431p5/6572605.jpg")

    def test_db_num(self):
        """This function test the correctness of the number of data in database"""
        database = scrape_to_db(2, 2)
        book_mongodb = database.get_collection("book_info")
        author_mongodb = database.get_collection("author_info")
        self.assertEqual(book_mongodb.find().count(), 10)
        self.assertEqual(author_mongodb.find().count(), 5)

    def test_db_item(self):
        """This function test the correctness of data in database"""
        client = MongoClient('localhost', 27017)
        database = client['sample_db']
        book_mongodb = database.get_collection("book_info")
        self.assertEqual(book_mongodb.find_one({'_id': 40597810})["book_title"], "Daisy Jones & The Six")

    def test_export_js(self):
        """This function test the validity of exported json file"""
        interface.export_js()
        self.assertEqual(is_json('data.json'), True)

    def test_input_url(self):
        """This function test the correctness of input url"""
        invalid_url = "dklsh"
        self.assertEqual(interface.check_url(invalid_url), 0)
        non_good_reads_url = "https://wiki.illinois.edu/wiki/pages/viewpage.action?pageId=616243854"
        self.assertEqual(interface.check_url(non_good_reads_url), 0)
        non_book_url = "https://www.goodreads.com/author/show/6572605.Taylor_Jenkins_Reid"
        self.assertEqual(interface.check_url(non_book_url), 0)

    def test_input_scrape_num(self):
        """This function test the correctness of input number of book or author"""
        # book number too large
        self.assertEqual(interface.check_s([300, 20]), 0)
        # both book number and author number too large
        self.assertEqual(interface.check_s([300, 200]), 0)
        # author number too large
        self.assertEqual(interface.check_s([30, 200]), 0)

    def test_input_js_(self):
        self.assertEqual(interface.check_js('ksdhf'), 0)

    def test_network_node(self):
        graph = network.create_network()
        self.assertEqual(len(list(graph.nodes)), 16)
        self.assertEqual(graph.has_node(40597810), True)

    def test_network_book_edge(self):
        graph = network.create_network()
        # edges between similar books
        self.assertEqual(graph.has_edge(40597810, 43923951), True)
        self.assertEqual(graph.has_edge(43923951, 44428668), True)

    def test_network_book_author_edge(self):
        graph = network.create_network()
        # edges between book and author
        self.assertEqual(graph.has_edge(50548197, 8730), True)


if __name__ == '__main__':
    unittest.main()
