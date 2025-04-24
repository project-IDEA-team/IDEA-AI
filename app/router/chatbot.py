from fastapi import APIRouter
from pydantic import BaseModel
from app.service.embedding import get_embedding
from app.service.mongodb import search_similar_policies
import openai
import os

router = APIRouter()

class QueryRequest(BaseModel):
    text: str

@router.post("/chatbot/query")
async def chatbot_query(req: QueryRequest):
    embedding = get_embedding(req.text)
    docs = search_similar_policies(embedding, limit=3)

    if not docs:
        return {"answer": "관련된 정보를 찾을 수 없습니다."}

    context = "\n\n---\n\n".join([doc["page_content"] for doc in docs])

    system_prompt = """
    너는 장애인 복지 제도와 고용 지원에 대해 상담해주는 따뜻한 전문가야.
    사용자는 '장애인 본인'이며, 어떤 지원금이나 도움을 받을 수 있는지 알고 싶어 해.
    사업주나 기관 대상 정책은 제외하고, 개인 장애인이 받을 수 있는 혜택 위주로 설명해줘.
    """

    user_prompt = f"""
다음 내용을 참고해서 답변해줘:

[정책 내용]
{context}

질문: {req.text}
"""

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    )

    return {
        "answer": completion.choices[0].message.content,
        "sources": [doc["metadata"]["url"] for doc in docs]
    }