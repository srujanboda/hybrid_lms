from pymongo import MongoClient

def get_db_handle():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["lms_mongo"]
    return db
 
