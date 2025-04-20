from pymongo import MongoClient
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
collection = client["kead_db"]["policies"]

def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

def search_similar_policy(query_vector):
    docs = list(collection.find({"embedding": {"$ne": None}}))
    scored = sorted(docs, key=lambda doc: cosine_similarity(query_vector, doc["embedding"]), reverse=True)
    return scored[0] if scored else {"body": "관련 정책 정보를 찾을 수 없습니다."}
