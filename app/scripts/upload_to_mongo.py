# ✅ 필요한 모듈 불러오기
from pymongo import MongoClient
import json
from dotenv import load_dotenv
import os
from uuid import uuid4
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ✅ .env 파일에서 MongoDB URI 불러오기
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# ✅ MongoDB 연결
client = MongoClient(MONGO_URI)
db = client["kead_db"]
collection = db["policy_chunks"]  # ← 저장할 컬렉션명

# ✅ 텍스트 Splitter 설정 (문단 → 문장 → 단어)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)

# ✅ 금액 정보가 포함된 표 단락만 추출
def extract_bonus_block(text):
    lines = text.split("\n")
    table_lines = [
        line.strip()
        for line in lines
        if any(keyword in line for keyword in ["만원", "지급단가", "경증장애인", "중증장애인", "남성", "여성"])
    ]
    return "\n".join(table_lines) if table_lines else None

# ✅ 문서 단위로 chunking 처리
def chunk_and_format(doc):
    body = doc.get("body", "")
    chunks = splitter.split_text(body)
    chunk_docs = []

    # 기본 chunk 처리
    for i, chunk in enumerate(chunks):
        chunk_docs.append({
            "_id": str(uuid4()),
            "doc_id": str(doc.get("_id", uuid4())),
            "chunk_index": i,
            "page_content": chunk,
            "metadata": {
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "category": doc.get("category", "")
            },
            "embedding": None
        })

    # 금액 정보 블록 추가 (별도로 추출해 마지막에 넣기)
    bonus_block = extract_bonus_block(body)
    if bonus_block:
        chunk_docs.append({
            "_id": str(uuid4()),
            "doc_id": str(doc.get("_id", uuid4())),
            "chunk_index": len(chunk_docs),
            "page_content": bonus_block,
            "metadata": {
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "category": doc.get("category", ""),
                "note": "지급단가 및 지원금 표 정보"
            },
            "embedding": None
        })

    return chunk_docs

# ✅ main 함수: 파일 읽고 → chunk → DB 저장
def main():
    file_path = "scripts/policies.json"

    if not os.path.exists(file_path):
        print(f"❌ JSON 파일을 찾을 수 없습니다: {file_path}")
        return

    with open(file_path, encoding="utf-8") as f:
        docs = json.load(f)

    all_chunks = []
    for doc in docs:
        chunks = chunk_and_format(doc)
        all_chunks.extend(chunks)

    if all_chunks:
        collection.insert_many(all_chunks)
        print(f"✅ 총 {len(all_chunks)}개의 chunk가 저장되었습니다.")
    else:
        print("❗ 저장할 chunk가 없습니다.")

# ✅ 실행
if __name__ == "__main__":
    main()
