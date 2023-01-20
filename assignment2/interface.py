"""
This module handle the command line interface.
"""
import argparse
import json

import validators
from flask import ctx
from pymongo import MongoClient

import scraping
import requests

import storing

START_URL = ""


def parsing():
    """This function add and parse the command"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', action='store', type=str, help='the url to search for')
    parser.add_argument('-js', action='store', type=str, help='the json file to read from')
    parser.add_argument('-s', action='store', nargs='+', type=int,
                        help='the number of books and authors to scrape')
    parser.add_argument('-ex', action='store_true', help='the book or author to export')
    parser.add_argument('-GET', action='store', type=str, help='the endpoint for GET')
    parser.add_argument('-PUT', action='store', type=str, help='the endpoint for PUT')
    parser.add_argument('-POST', action='store', type=str, help='the endpoint for POST')
    parser.add_argument('-DELETE', action='store', type=str, help='the endpoint for DELETE')
    args = parser.parse_args()

    if args.GET is not None:
        call_api_get(args.GET)
        return
    if args.PUT is not None:
        call_api_put(args.PUT)
        return
    if args.POST is not None:
        call_api_post(args.POST)
        return
    if args.DELETE is not None:
        call_api_delete(args.DELETE)
        return

    if args.url is not None:
        check_url(args.url)
        return
    if args.js is not None:
        check_js(args.js)
        return
    if args.s is not None:
        check_s(args.s)
        return
    if args.ex is not None:
        export_js()
        return
    return args


def check_url(input_url):
    """This function check the input url"""
    valid = validators.url(input_url)
    if not valid:
        print("Invalid url! Please enter a new valid url!")
        return 0
    if "goodreads" not in input_url:
        print("Not a GoodReads url! Please enter a GoodReads url!")
        return 0
    if "book" not in input_url:
        print("Not a book url! Please enter a book url!")
        return 0

    global START_URL
    START_URL = input_url
    return 1


def check_js(input_js):
    """This function check the input json file"""
    # validity check of the command
    file = open(input_js, "r")
    try:
        data = json.loads(file.read())
    except ValueError as e:
        print("Invalid json file! Please enter a new valid json file!")
        return 0
    if isinstance(data) is not dict or data["book_mongodb"][0]["_id"] or \
            data["author_mongoDB"][0]["_id"] is None:
        print("Malformed data structure! Please enter a new valid json file!")
        return 0
    create_and_update(data)
    file.close()
    return 1


def check_s(input_s):
    """This function check the input book number and author number to scrape"""
    # validity check of the command
    book_num = input_s[0]
    auth_num = input_s[1]
    if book_num > 200 or auth_num > 50:
        print("Book number or author number too large! Please enter a valid number!")
        return 0
    # implementation of the command
    storing.scrape_and_store(storing.create_mongo_db(), START_URL, book_num, auth_num)
    return 1


def export_js():
    """This function export the data from database into json file"""
    # implementation of the command
    client = MongoClient('localhost', 27017)
    exist_db = client['good_reads']
    book_mongodb = exist_db.get_collection("book_info")
    author_mongodb = exist_db.get_collection("author_info")
    dict_cur = {}
    book_lis_cur = list(book_mongodb.find())
    auth_lis_cur = list(author_mongodb.find())
    dict_cur["book_mongodb"] = book_lis_cur
    dict_cur["author_mongodb"] = auth_lis_cur
    json_data = json.dumps(dict_cur, indent=2)
    with open('data.json', 'w') as file:
        file.write(json_data)
    file.close()


def create_and_update(data):
    """This function create or update data in database"""
    client = MongoClient('localhost', 27017)
    exist_db = client['good_reads']
    book_mongodb = exist_db.get_collection("book_info")
    author_mongodb = exist_db.get_collection("author_info")
    search_in_database(book_mongodb, data['book_mongodb'], "book")
    search_in_database(author_mongodb, data['author_mongoDB'], "author")


def search_in_database(collection, js_data, obj_str):
    """This function search for create or update"""
    for item in js_data:
        searched_data = collection.find_one({"_id": item["_id"]})
        if searched_data is None:
            collection.insert_one(item)
            print("A new " + obj_str + " has been created!" + item)
        elif searched_data is not None and item != searched_data:
            collection.update(searched_data, item)
            print("A " + obj_str + " has been updated!" + item)


def call_api_get(get_url):
    response = requests.get("http://127.0.0.1:5000/" + get_url)
    print_response_status(response, "get")


def print_response_status(response, method):
    if response.status_code == 200:
        print("Successful " + method + "!")
    elif response.status_code == 404:
        print('Not Found.')


def call_api_put(put_url):
    response = requests.put("http://127.0.0.1:5000/" + put_url)
    print_response_status(response, "put")


def call_api_post(post_url):
    file = open("data.json", "r")
    try:
        data = json.loads(file.read())
    except ValueError as e:
        print("Invalid json file! Please enter a new valid json file!")
        return 0
    response = requests.post("http://127.0.0.1:5000/" + post_url, json=data)
    print_response_status(response, "post")


def call_api_delete(del_url):
    response = requests.delete("http://127.0.0.1:5000/" + del_url)
    print_response_status(response, "delete")
