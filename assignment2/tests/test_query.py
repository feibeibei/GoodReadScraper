"""test the usage of query"""
import unittest

from pymongo import MongoClient

import query


def get_db():
    """get the existing database"""
    client = MongoClient('localhost', 27017)
    exist_db = client['good_reads']
    return exist_db


class TestScraping(unittest.TestCase):
    def test_exact(self):
        """test exact value of a field"""
        find_content = query.contain_operator("book.id:\"40597810\"")
        book_mongodb = get_db().get_collection("book_info")
        found_item = book_mongodb.find_one(find_content)
        self.assertEqual(found_item, book_mongodb.find_one({"id": "40597810"}))

    def test_regex(self):
        """test regex value of a field"""
        find_content = query.contain_operator("book.id:405978")
        book_mongodb = get_db().get_collection("book_info")
        found_item = book_mongodb.find_one(find_content)
        self.assertEqual(found_item, book_mongodb.find_one({"id": "40597810"}))

    def test_id_lt(self):
        """test less than in id"""
        find_content = query.contain_operator("book.id:<40597811")
        book_mongodb = get_db().get_collection("book_info")
        found_item = book_mongodb.find_one(find_content)
        self.assertEqual(found_item, book_mongodb.find_one({"id": {"$lt": "40597810"}}))

    def test_rate_lt(self):
        """test less than in rate"""
        find_content = query.contain_operator("book.rating:<4.3")
        book_mongodb = get_db().get_collection("book_info")
        found_item = book_mongodb.find_one(find_content)
        self.assertEqual(found_item, book_mongodb.find_one({"rating": {"$lt": "4.3"}}))

    def test_id_gt(self):
        """test greater than in id"""
        find_content = query.contain_operator("book.id:>40597809")
        book_mongodb = get_db().get_collection("book_info")
        found_item = book_mongodb.find_one(find_content)
        self.assertEqual(found_item, book_mongodb.find_one({"id": {"$gt": "40597809"}}))

    def test_rate_gt(self):
        """test greater than in rating"""
        find_content = query.contain_operator("book.rating:>4.0")
        book_mongodb = get_db().get_collection("book_info")
        found_item = book_mongodb.find_one(find_content)
        self.assertEqual(found_item, book_mongodb.find_one({"rating": {"$gt": "4.0"}}))

    def test_ne(self):
        """test negating value of a field"""
        find_content = query.contain_operator("book.id:NOT40597810")
        book_mongodb = get_db().get_collection("book_info")
        found_item = book_mongodb.find_one(find_content)
        self.assertEqual(found_item, book_mongodb.find_one({"id": {"$ne": "40597810"}}))

    def test_and(self):
        """test and logic"""
        found_item = query.logic_operator("AND", "book.id:405978ANDbook.rating:>4.0", "$and")
        book_mongodb = get_db().get_collection("book_info")
        self.assertEqual(found_item, book_mongodb.find_one({"id": "40597810"}))

    def test_or(self):
        """test or logic"""
        found_item = query.logic_operator("OR", "book.id:\"40597810\"ORbook.rating:4.0", "$or")
        book_mongodb = get_db().get_collection("book_info")
        self.assertEqual(found_item, book_mongodb.find_one({"$or": [{"id": "40597810"}, {"rating": {"$gt": "4.0"}}]}))


if __name__ == '__main__':
    unittest.main()
