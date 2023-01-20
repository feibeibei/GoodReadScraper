"""
This module handle the API.
"""
from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient

import query
import scraping
from flask_cors import CORS

import storing

app = Flask(__name__, static_folder="client")
CORS(app)


def get_db():
    """This function get database"""
    client = MongoClient('localhost', 27017)
    exist_db = client['good_reads']
    return exist_db


def get_id_and_col(item):
    """This function get id and collection"""
    item_id = int(request.args.get('id'))
    exist_db = get_db()
    collection = exist_db.get_collection(item + "_info")
    return item_id, collection


@app.route('/')
def index():
    return render_template('api.html')


@app.route('/api/book', methods=['GET'])
def get_book():
    """This function get book"""
    book_id, book_mongodb = get_id_and_col("book")
    target_book = book_mongodb.find_one({"_id": book_id})
    if target_book is None:
        return "No such id is found!"
    return jsonify(target_book)


@app.route('/vis/top-books', methods=['GET'])
def get_book_rank():
    book_mongodb = get_db().get_collection("book_info")
    k = int(request.args.get('k'))
    rank = book_mongodb.find().sort("rating", -1)
    item_list = []
    i = 0
    for item in rank:
        if i >= k:
            break
        item_list.append(item)
        i += 1
    return jsonify(item_list)


@app.route('/api/book', methods=['PUT'])
def put_book():
    """This function put book"""
    book_id, book_mongodb = get_id_and_col("book")
    target_book = book_mongodb.find_one({"_id": book_id})
    js_content = request.get_json(force=True)
    if target_book is None:
        return "No such id is found!"
    if type(js_content) is list:
        return "Json file is mal-structured!"
    for k, v in js_content.items():
        book_mongodb.update_one({k: target_book[k]}, {'$set': {k: v}})
    return "Successfully put!"


@app.route('/api/book', methods=['POST'])
def post_book():
    """This function post book"""
    book_id, book_mongodb = get_id_and_col("book")
    js_content = request.get_json(force=True)
    if type(js_content) is list:
        return "Json file is mal-structured!"
    book_mongodb.insert_one(js_content)
    return "Successfully posted!"


@app.route('/api/book', methods=['DELETE'])
def del_book():
    """This function delete book"""
    book_id, book_mongodb = get_id_and_col("book")
    book_mongodb.delete_one({"_id": book_id})
    return "Successfully deleted!"


@app.route('/api/books', methods=['POST'])
def post_books():
    """This function post books"""
    exist_db = get_db()
    book_mongodb = exist_db.get_collection("book_info")
    js_content = request.get_json(force=True)
    for book in js_content:
        book_mongodb.insert_one(book)
    return 'Successfully posted!'


@app.route('/api/author', methods=['GET'])
def get_author():
    """This function get author"""
    author_id, author_mongodb = get_id_and_col("author")
    target_author = author_mongodb.find_one({"_id": author_id})
    if target_author is None:
        return "No such id is found!"
    return jsonify(target_author)


@app.route('/vis/top-authors', methods=['GET'])
def get_auth_rank():
    author_mongodb = get_db().get_collection("author_info")
    k = int(request.args.get('k'))
    rank = author_mongodb.find().sort("rating", -1)
    item_list = []
    i = 0
    for item in rank:
        if i >= k:
            break
        item_list.append(item)
        i += 1
    return jsonify(item_list)


@app.route('/api/author', methods=['PUT'])
def put_author():
    """This function put author"""
    author_id, author_mongodb = get_id_and_col("author")
    target_author = author_mongodb.find_one({"_id": author_id})
    if target_author is None:
        return "No such id is found!"
    js_content = request.get_json(force=True)
    if type(js_content) is list:
        return "Json file is mal-structured!"
    for k, v in js_content.iteritems():
        author_mongodb.update_one({k: target_author[k]}, {'$set': {k: v}})
    return "Successfully put!"


@app.route('/api/author', methods=['POST'])
def post_author():
    """This function post author"""
    author_id, author_mongodb = get_id_and_col("author")
    js_content = request.get_json(force=True)
    if type(js_content) is list:
        return "Json file is mal-structured!"
    author_mongodb.insert_one(js_content)
    return "Successfully posted!"


@app.route('/api/author', methods=['DELETE'])
def del_author():
    """This function delete author"""
    author_id, author_mongodb = get_id_and_col("author")
    author_mongodb.delete_one({"_id": author_id})
    return "Successfully deleted!"


@app.route('/api/authors', methods=['POST'])
def post_authors():
    """This function post authors"""
    exist_db = get_db()
    author_mongodb = exist_db.get_collection("author_info")
    js_content = request.get_json(force=True)
    for author in js_content:
        author_mongodb.insert_one(author)
    return 'Successfully posted!'


@app.route('/api/scrape', methods=['POST'])
def post_scrape():
    """This function post scraped result"""
    exist_db = get_db()
    attr = request.args.get('attr')
    url = "https://www.goodreads.com/" + attr
    if "book" in attr:
        storing.scrape_and_store(exist_db, url, 1, 0)
        return "Successfully posted!"
    if "author" in attr:
        new_scraper = scraping.Scraper()
        author = new_scraper.scrape_a_auth_url(url)
        new_scraper.scraping_related_author(author)
        author_mongodb = exist_db.get_collection("author_info")
        author_mongodb.insert_one(author)
        return "Successfully posted!"


@app.route('/api/search', methods=['GET'])
def search():
    """This function get searched result"""
    query_str = str(request.args.get('q'))
    exist_db = get_db()
    collection_name = query_str.split('.')[0] + "_" + "info"
    data_col = exist_db.get_collection(collection_name)
    if "." not in query_str or ":" not in query_str:
        print_mal_query()
    if "AND" in query_str:
        target_obj = query.logic_operator("AND", query_str, "$and")
        return jsonify(target_obj)
    if "OR" in query_str:
        target_obj = query.logic_operator("OR", query_str, "$or")
        return jsonify(target_obj)
    if ":" in query_str:
        obj = data_col.find_one(query.contain_operator(query_str))
        return jsonify(obj)


def print_mal_query():
    """This function print malformed query"""
    print("The input is a malformed query string!")


if __name__ == '__main__':
    app.run(debug=True)
