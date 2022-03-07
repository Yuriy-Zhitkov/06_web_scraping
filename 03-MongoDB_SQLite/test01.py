from pprint import pprint

import pymongo


def print_mongo_docs(cursor):
    for doc in cursor:
        pprint(doc)


MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "db_hh_vac"
MONGO_COLLECTION = "01"


with pymongo.MongoClient(MONGO_HOST, MONGO_PORT) as client:
    db = client[MONGO_DB]
    collections = db[MONGO_COLLECTION]

    # collections.insert_one({'name': 'Nick', 'age': 20, 'item': 'bike'})
    # collections.insert_one({'name': 'Kate', 'age': 19, 'item': 'car'})
    # collections.insert_one({'name': 'Mike', 'age': 22, 'item': 'serf'})

    # cursor = collections.find()
    # print_mongo_docs(cursor)

    a = collections.count_documents({})
    print(a)

    cursor02 = collections.find({"salary_min": {"$gt": 30000}})
    print(len(list(cursor02)))
    # print_mongo_docs(cursor02)
