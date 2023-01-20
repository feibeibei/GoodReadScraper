"""Test api"""
import json
import os
import tempfile

import flask
import pytest
import requests
from pymongo import MongoClient

import api


def get_db():
    """Get existing database"""
    client = MongoClient('localhost', 27017)
    exist_db = client['good_reads']
    return exist_db


@pytest.fixture
def client():
    """Create client"""
    db_fd, api.app.config['DATABASE'] = tempfile.mkstemp()
    api.app.config['TESTING'] = True

    with api.app.test_client() as client:
        with api.app.app_context():
            api.get_db()
        yield client

    os.close(db_fd)
    os.unlink(api.app.config['DATABASE'])


def test_get_book_invalid(client):
    """Test when book id does not exist"""
    rv = client.get('http://127.0.0.1:5000/api/book?id=123')
    assert b"No such id is found!" in rv.data


def test_get_author_invalid(client):
    """Test when author id does not exist"""
    rv = client.get('http://127.0.0.1:5000/api/author?id=123')
    assert b"No such id is found!" in rv.data


def test_post_book_valid():
    """Test valid book post"""
    file = open("../data.json", "r")
    data = json.loads(file.read())
    response = requests.post('http://127.0.0.1:5000/api/book?id=40597810', json=data)
    assert b"Successfully posted!" in response.content


def test_post_author_valid():
    """Test valid author post"""
    file = open("../data.json", "r")
    data = json.loads(file.read())
    response = requests.post('http://127.0.0.1:5000/api/author?id=18257829', json=data)
    assert b"Successfully posted!" in response.content


def test_put_book_invalid():
    """Test when book id does not exist"""
    file = open("../data.json", "r")
    data = json.loads(file.read())
    response = requests.put('http://127.0.0.1:5000/api/book?id=123', json=data)
    assert b"No such id is found!" in response.content


def test_put_author_invalid():
    """Test when author id does not exist"""
    file = open("../data.json", "r")
    data = json.loads(file.read())
    response = requests.put('http://127.0.0.1:5000/api/author?id=123', json=data)
    assert b"No such id is found!" in response.content


def test_put_book_valid():
    """Test valid book put"""
    response = requests.put('http://127.0.0.1:5000/api/book?id=40597810', json={"ISBN": "1234567890"})
    assert b"Successfully put!" in response.content


def test_put_author_valid():
    """Test valid author put"""
    response = requests.put('http://127.0.0.1:5000/api/author?id=18257829', json={"rating": "3.0"})
    assert b"Successfully put!" in response.content


def test_del_book_valid():
    """Test valid book delete"""
    response = requests.delete('http://127.0.0.1:5000/api/book?id=40597810')
    assert b"Successfully deleted!" in response.content


def test_del_author_valid():
    """Test valid author delete"""
    response = requests.delete('http://127.0.0.1:5000/api/author?id=18257829')
    assert b"Successfully deleted!" in response.content


def test_search_context(client):
    """Test the casting of query"""
    app = flask.Flask(__name__)
    with app.test_request_context('/?q=book.id%3A123'):
        assert flask.request.path == '/'
        assert flask.request.args['q'] == 'book.id:123'


