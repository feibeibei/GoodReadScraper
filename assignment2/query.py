"""
This module query and parsing.
"""
import re

from pymongo import MongoClient


def get_db():
    """This function return the existing database"""
    client = MongoClient('localhost', 27017)
    exist_db = client['good_reads']
    return exist_db


def print_field_error():
    """This function print field error"""
    print("The field is not defined!")


def print_enclose_error():
    """This function print enclose error"""
    print("The query is not enclosed properly!")


def print_mal_query():
    """This function print malformed query"""
    print("The input is a malformed query string!")


def print_no_conj():
    """This function print no conjunction error"""
    print("The logic operator is not in conjunction with key words")


def contain_operator(query):
    """This function return the find syntax for pymong"""
    check_query(query)
    query_list = query.split('.')
    exist_db = get_db()
    collection_name = query_list[0] + "_" + "info"
    col = exist_db.get_collection(collection_name)
    contain_list = re.split(':', query_list[1])
    field = contain_list[0]
    value = contain_list[1]
    # Bonus for wild card operator *
    # data_col.create_index({"Desc": "wild"})
    if field == "*":
        field = "$wild"
    if field not in set(col.find_one().keys()):
        print_field_error()
        return 0
    if '"' in query:
        if query.count("\"") is not 2:
            print_enclose_error()
            return 0
        content = contain_list[1].replace('"', '/')
        value = re.split('/', content)[1]
        return {field: value}
    if "<" in query:
        value = re.split('<', contain_list[1])[1]
        return {field: {"$lt": value}}
    if ">" in query:
        value = re.split('>', contain_list[1])[1]
        return {field: {"$gt": value}}
    if "NOT" in query:
        value = re.split('NOT', contain_list[1])[1]
        return {field: {"$ne": value}}

    return {field: {"$regex": value}}


def logic_operator(keyword, query, logic):
    """This function return logic results"""
    query_list = re.split(keyword, query)
    query_1 = query_list[0]
    query_2 = query_list[1]
    if check_query(query_1) is 0 or check_query(query_2) is 0:
        print_no_conj()
    exist_db = get_db()
    collection_name = query_1.split('.')[0] + "_" + "info"
    data_col = exist_db.get_collection(collection_name)
    return data_col.find_one({logic: [contain_operator(query_1), contain_operator(query_2)]})


def check_query(query):
    """This function check query style"""
    if "." not in query or ":" not in query:
        print_mal_query()
        return 0
    return 1

