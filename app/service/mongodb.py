# mongodb.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import numpy as np
import traceback

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["kead_db"]
collection = db["policy_chunks"]

# ✅ 1. Atlas Search 기반 키워드 검색
def search_chunks_by_keyword(keyword: str, limit: int = 5):
    try:
        pipeline = [
            {
                "$search": {
                    "index": "default",
                    "text": {
                        "query": keyword,
                        "path": ["page_content", "metadata.title"]
                    }
                }
            },
            { "$limit": limit }
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        print("==== [mongodb.py] 키워드 검색 에러 ====")
        print(e)
        traceback.print_exc()
        return []


# ✅ 2. 벡터 임베딩 기반 유사도 검색 (GPT 응답용)
def search_similar_policies(query_vector, limit=3):
    try:
        documents = list(collection.find({"embedding": {"$ne": None}}))
        scores = []
        for doc in documents:
            doc_vector = doc["embedding"]
            score = cosine_similarity(query_vector, doc_vector)
            scores.append((doc, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scores[:limit]]
    except Exception as e:
        print("==== [mongodb.py] 유사도 검색 에러 ====")
        print(e)
        traceback.print_exc()
        return []



# ✅ 3. 코사인 유사도 계산 함수
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
