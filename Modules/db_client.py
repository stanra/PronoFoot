from pymongo import MongoClient


def get_db(db_name):
    return MongoClient()[db_name]

def get_collection(db_name, col_name):
    return get_db(db_name)[col_name]


