"""
This module scrape book and author information from GoodReads into mongoDB database.
"""
import os
import re
from time import sleep
from urllib.request import urlopen

from bs4 import BeautifulSoup
from pymongo import MongoClient


def split_book_author(title):
    """This function split the "book by author" string scraped from GoodReads into book title
    and author name."""
    return title.split(" by ")


def print_info_log(obj):
    """This function prints progress/error log while scraping each book"""
    for k in obj.keys():
        if obj[k] is None:
            print("Could not find " + k)
        else:
            print("Found " + k + "!")
    return obj


def print_scrape_log(obj, loop_num):
    """This function prints scraping progress log"""
    print("*" * 50)
    print("Scraping " + obj + " " + loop_num)
    print("*" * 50)


class Scraper:
    def __init__(self):
        self.book_url_set = set()
        self.author_url_set = set()
        self.auth_counter = 0

    # # the set containing all the url of books that are scraped
    # BOOK_URL_SET = set()
    # # the set containing all the url of authors that are scraped
    # AUTHOR_URL_SET = set()
    # # keep track of the number of author that are scraped
    # AUTH_COUNTER = 0

    def scraping_book(self, book_url):
        """This function scrape book information from GoodReads into a book dictionary"""
        self.book_url_set.add(book_url)
        book_html = urlopen(book_url).read().decode("utf-8")
        book_soup = BeautifulSoup(book_html, "html.parser")
        book_title = split_book_author(book_soup.title.string)[0]
        new_book = {}
        new_book["book_title"] = book_title
        new_book["book_url"] = book_url
        new_book["_id"] = int(book_soup.find('input', {'id': 'book_id'}).get('value'))
        new_book["id"] = str(new_book["_id"])
        new_book["ISBN"] = book_soup.find("meta", property='books:isbn').attrs['content']
        new_book["author_url"] = book_soup.find("meta", property='books:author').attrs['content']
        new_book["author_name"] = split_book_author(book_soup.title.string)[1]
        new_book["image_url"] = book_soup.find("meta", property='og:image').attrs['content']
        new_book["rating_count"] = book_soup.find(itemprop="ratingCount").get("content")
        new_book["review_count"] = book_soup.find(itemprop="reviewCount").get("content")
        rating_num_list = re.findall(r'\d+', str(book_soup.find(itemprop="ratingValue").get_text))
        new_book["rating"] = rating_num_list[0] + "." + rating_num_list[1]
        new_book["similar_url"] = book_soup.find_all(class_="actionLink right seeMoreLink")[0]['href']
        return new_book

    def scraping_author(self, book):
        """This function scrape author information from GoodReads into a author dictionary"""
        # check if the author has already been scraped
        if book["author_url"] in self.author_url_set:
            return None

        new_author = {}
        self.author_url_set.add(book["author_url"])
        author_html = urlopen(book["author_url"]).read().decode("utf-8")
        author_soup = BeautifulSoup(author_html, "html.parser")
        new_author["author_name"] = book["author_name"]
        new_author["author_url"] = book["author_url"]
        new_author["_id"] = int(str(re.findall(r'\d+', book["author_url"])[0]))
        new_author["id"] = str(new_author["_id"])
        new_author["image_url"] = author_soup.find(itemprop="image").get("content")
        new_author["rating_count"] = author_soup.find(itemprop="ratingCount").get("content")
        new_author["review_count"] = author_soup.find(itemprop="reviewCount").get("content")
        rating_num_list = re.findall(r'\d+', str(author_soup.find(itemprop="ratingValue").get_text))
        new_author["rating"] = rating_num_list[0] + "." + rating_num_list[1]
        links = []
        for link in author_soup.findAll('a', href=True, text=True):
            links.append(link['href'])
        for link in links:
            if link.find("author/similar") != -1:
                new_author["related_url"] = "https://www.goodreads.com/" + link

        new_author["author_books"] = []
        new_author["author_books"].append(book["book_url"])
        self.auth_counter += 1
        return new_author

    def scrape_a_auth_url(self, auth_url):
        new_author = {}
        self.author_url_set.add(auth_url)
        author_html = urlopen(auth_url).read().decode("utf-8")
        author_soup = BeautifulSoup(author_html, "html.parser")
        new_author["author_name"] = author_soup.find("meta", property='og:title').attrs['content']
        new_author["author_url"] = auth_url
        new_author["_id"] = int(str(re.findall(r'\d+', auth_url)[0]))
        new_author["id"] = str(new_author["_id"])
        new_author["image_url"] = author_soup.find(itemprop="image").get("content")
        new_author["rating_count"] = author_soup.find(itemprop="ratingCount").get("content")
        new_author["review_count"] = author_soup.find(itemprop="reviewCount").get("content")
        rating_num_list = re.findall(r'\d+', str(author_soup.find(itemprop="ratingValue").get_text))
        new_author["rating"] = rating_num_list[0] + "." + rating_num_list[1]
        links = []
        for link in author_soup.findAll('a', href=True, text=True):
            links.append(link['href'])
        for link in links:
            if link.find("author/similar") != -1:
                new_author["related_url"] = "https://www.goodreads.com/" + link
            if link.find("book/show") != -1:
                new_author["author_books"] = []
                new_author["author_books"].append(link)
                break

        return new_author

    def scraping_related_author(self, new_author):
        """This function scrape the related author information"""
        url = new_author["related_url"]
        related_html = urlopen(url).read().decode("utf-8")
        related_soup = BeautifulSoup(related_html, "html.parser")
        links = []
        new_author["related_authors"] = []
        for link in related_soup.findAll('a', href=True, text=True):
            links.append(link['href'])
        for link in links:
            if link.find("https://www.goodreads.com/author/show") != -1:
                if link not in self.author_url_set:
                    new_author["related_authors"].append(link)

    def scraping_similar_book(self, new_book):
        """This function scrape the similar book information"""
        url = new_book["similar_url"]
        similar_html = urlopen(url).read().decode("utf-8")
        similar_soup = BeautifulSoup(similar_html, "html.parser")
        links = []
        for link in similar_soup.findAll('a', href=True, text=True):
            links.append(link['href'])
        new_book["similar_books"] = []
        for link in links:
            if link.find("/book/show") != -1:
                similar_book_url = link
                if similar_book_url.find("https://www.goodreads.com") == -1:
                    similar_book_url = "https://www.goodreads.com" + similar_book_url

                if similar_book_url not in self.book_url_set:
                    new_book["similar_books"].append(similar_book_url)

    # def create_mongo_db():
    #     """This function create a mongoDB database"""
    #     client = MongoClient('localhost', 27017)
    #     user_name = os.getenv("USERNAME")
    #     password = os.getenv("PASSWORD")
    #     client.testdb.add_user(str(user_name), str(password), roles=[{'role': 'readWrite', 'db': 'testdb'}])
    #     database = client['good_reads']
    #     database.drop_collection("book_info")
    #     database.drop_collection("author_info")
    #     database.create_collection("book_info")
    #     database.create_collection("author_info")
    #     return database
    #
    # def scrape_and_store(database, start_url, book_num, author_num):
    #     """This function store data into database while scraping"""
    #     book_mongodb = database.get_collection("book_info")
    #     author_mongodb = database.get_collection("author_info")
    #     url = start_url
    #     global AUTH_COUNTER
    #     for i in range(book_num):
    #         print_scrape_log("Book", str(i + 1))
    #         book = scraping_book(url)
    #         scraping_similar_book(book)
    #         print_info_log(book)
    #         book_mongodb.insert_one(book)
    #         if AUTH_COUNTER <= author_num:
    #             author = scraping_author(book)
    #             if author is not None:
    #                 print_scrape_log("Author", str(AUTH_COUNTER))
    #                 scraping_related_author(author)
    #                 print_info_log(author)
    #                 author_mongodb.insert_one(author)
    #         sleep(5)
    #         url = book["similar_books"][0]
