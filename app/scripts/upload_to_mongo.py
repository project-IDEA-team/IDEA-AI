from pymongo import MongoClient
import json
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["kead_db"]
collection = db["policies"]

with open("scripts/policies.json", encoding="utf-8") as f:
    docs = json.load(f)
    collection.insert_many(docs)
