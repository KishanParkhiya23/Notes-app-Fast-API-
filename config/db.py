from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/notes"

conn = MongoClient(MONGO_URI)

