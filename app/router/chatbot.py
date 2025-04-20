from fastapi import APIRouter
from pydantic import BaseModel
from app.service.embedding import get_embedding
from app.service.mongodb import search_similar_policy
import openai
import os

router = APIRouter()

class QueryRequest(BaseModel):
    text: str

@router.post("/chatbot/query")
async def chatbot_query(req: QueryRequest):
    embedding = get_embedding(req.text)
    doc = search_similar_policy(embedding)
    prompt = f"다음 내용을 참고하여 요약해줘:\n{doc['body']}"

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"answer": completion.choices[0].message.content}
