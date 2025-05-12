# mongodb.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import MONGODB_URL

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["kead_db"]
collection = db["policy_chunks"]

logger = logging.getLogger(__name__)

class MongoDBClient:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client.kead_db
    
    async def save_chat_history(
        self,
        user_id: str,
        messages: List[Dict[str, Any]],
        user_type: str
    ) -> bool:
        """
        대화 이력을 저장합니다.
        
        Args:
            user_id: 사용자 ID
            messages: 대화 메시지 목록
            user_type: 사용자 유형
            
        Returns:
            저장 성공 여부
        """
        try:
            chat_record = {
                "user_id": user_id,
                "user_type": user_type,
                "messages": messages,
                "timestamp": datetime.utcnow()
            }
            
            await self.db.chat_history.insert_one(chat_record)
            return True
            
        except Exception as e:
            logger.error(f"대화 이력 저장 중 오류 발생: {str(e)}")
            return False
    
    async def get_chat_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        사용자의 대화 이력을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            limit: 조회할 최대 대화 수
            
        Returns:
            대화 이력 목록
        """
        try:
            cursor = self.db.chat_history.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            chat_history = []
            async for doc in cursor:
                # ObjectId를 문자열로 변환
                doc["_id"] = str(doc["_id"])
                chat_history.append(doc)
            
            return chat_history
            
        except Exception as e:
            logger.error(f"대화 이력 조회 중 오류 발생: {str(e)}")
            return []

    async def delete_chat_history(self, user_id: str) -> bool:
        """
        사용자의 대화 이력을 삭제합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            result = await self.db.chat_history.delete_many({"user_id": user_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"대화 이력 삭제 중 오류 발생: {str(e)}")
            return False

# ✅ 1. Atlas Search 기반 키워드 검색
def search_chunks_by_keyword(keyword: str, limit: int = 5):
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


# ✅ 2. 벡터 임베딩 기반 유사도 검색 (GPT 응답용)
def search_similar_policies(query_vector, limit=3):
    documents = list(collection.find({"embedding": {"$ne": None}}))
    scores = []

    for doc in documents:
        doc_vector = doc["embedding"]
        score = cosine_similarity(query_vector, doc_vector)
        scores.append((doc, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in scores[:limit]]



# ✅ 3. 코사인 유사도 계산 함수
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

# ✅ 4. public_data_db 복지 서비스 목록 검색

def search_welfare_services(keyword: str = "", limit: int = 5):
    db = client["public_data_db"]
    col = db["welfare_service_list"]
    if keyword:
        query = {
            "$or": [
                {"servNm": {"$regex": keyword, "$options": "i"}},
                {"jurMnofNm": {"$regex": keyword, "$options": "i"}},
                {"servDgst": {"$regex": keyword, "$options": "i"}}
            ]
        }
    else:
        query = {}
    return list(col.find(query).limit(limit))

# ✅ 5. public_data_db 복지 서비스 상세 조회

def get_welfare_service_detail(servId: str):
    db = client["public_data_db"]
    col = db["welfare_service_detail"]
    return col.find_one({"servId": servId})

# ✅ 6. public_data_db 장애인 구직 현황 검색

def search_disabled_job_offers(keyword: str = "", limit: int = 5):
    db = client["public_data_db"]
    col = db["disabled_job_offers"]
    if keyword:
        query = {
            "$or": [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"company": {"$regex": keyword, "$options": "i"}},
                {"location": {"$regex": keyword, "$options": "i"}}
            ]
        }
    else:
        query = {}
    return list(col.find(query).limit(limit))
