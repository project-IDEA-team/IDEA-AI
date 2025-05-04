from openai import OpenAI
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["kead_db"]
collection = db["policy_chunks"]

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str):
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print("==== [embedding.py] 임베딩 에러 ====")
        print(e)
        traceback.print_exc()
        raise

print("💡 아직 임베딩되지 않은 문서 수:", collection.count_documents({"embedding": None}))
def fill_embeddings():
    chunks = collection.find({"embedding": None})
    for chunk in chunks:
        print("🔍 처리 중:", chunk["metadata"]["title"])
        text = chunk.get("page_content", "")
        if not text.strip():
            continue
        try:
            response = openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embedding = response.data[0].embedding
            collection.update_one({"_id": chunk["_id"]}, {"$set": {"embedding": embedding}})
            print(f"✅ 임베딩 완료: {chunk['metadata']['title'][:30]}...")
        except Exception as e:
            import traceback
            print(f"❌ 에러: {e}")

if __name__ == "__main__":
    fill_embeddings()