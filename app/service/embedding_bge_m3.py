from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["kead_db"]
collection = db["policy_chunks"]

# BGE-M3 모델 초기화
model = SentenceTransformer('BAAI/bge-m3')

def get_embedding(text: str):
    """
    텍스트를 BGE-M3 모델을 사용하여 임베딩합니다.
    """
    return model.encode(text).tolist()

def fill_embeddings():
    """
    임베딩이 없는 문서들에 대해 임베딩을 생성하고 저장합니다.
    """
    chunks = collection.find({"embedding": None})
    for chunk in chunks:
        print("🔍 처리 중:", chunk["metadata"]["title"])
        text = chunk.get("page_content", "")
        if not text.strip():
            continue
        try:
            embedding = get_embedding(text)
            collection.update_one({"_id": chunk["_id"]}, {"$set": {"embedding": embedding}})
            print(f"✅ 임베딩 완료: {chunk['metadata']['title'][:30]}...")
        except Exception as e:
            import traceback
            print(f"❌ 에러: {e}")

if __name__ == "__main__":
    fill_embeddings() 