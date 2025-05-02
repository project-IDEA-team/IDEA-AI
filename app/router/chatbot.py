from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.service.embedding import get_embedding
from app.service.mongodb import search_similar_policies
import openai
import os
import logging
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class Source(BaseModel):
    url: str
    name: str

class PolicyCard(BaseModel):
    id: str
    title: str
    summary: str
    type: str
    details: str
    imageUrl: Optional[str] = None
    source: Optional[Source] = None

class QueryRequest(BaseModel):
    text: str

class ChatbotResponse(BaseModel):
    answer: str
    cards: List[PolicyCard]

@router.post("/chatbot/query")
async def chatbot_query(req: QueryRequest):
    # 단순 인사 패턴 체크
    greetings = ["안녕", "안녕하세요", "hi", "hello", "ㅎㅇ", "하이"]
    if any(req.text.lower().strip() == g for g in greetings):
        return ChatbotResponse(
            answer="안녕하세요! 장애인 복지 제도와 고용 지원에 대해 궁금하신 점이 있으시다면 언제든 물어보세요.",
            cards=[]
        )

    # 정책 검색 및 응답 생성
    embedding = get_embedding(req.text)
    docs = search_similar_policies(embedding, limit=3)

    # 검색된 문서를 카드 형식으로 변환
    cards = []
    relevant_docs = [doc for doc in docs if "전화" not in doc["page_content"]]

    if not relevant_docs:
        return ChatbotResponse(
            answer="죄송합니다. 현재 영등포구의 청각장애인을 위한 구체적인 정책 정보를 찾지 못했습니다. 더 정확한 정보를 위해서는 영등포구청 장애인복지과(☎ 02-2670-3111)로 문의해주시면 자세히 안내받으실 수 있습니다.",
            cards=[]
        )

    for doc in relevant_docs:
        card = PolicyCard(
            id=str(uuid.uuid4()),
            title=doc["metadata"].get("title", "정책 정보"),
            summary=doc["page_content"][:100] + "...",
            type="policy",
            details=doc["page_content"],
            imageUrl=doc["metadata"].get("imageUrl", "https://www.kead.or.kr/common/images/logo_kead.png"),
            source=Source(
                url=doc["metadata"].get("url", ""),
                name="한국장애인고용공단"
            )
        )
        cards.append(card)

    context = "\n\n---\n\n".join([doc["page_content"] for doc in relevant_docs])
    
    # 프롬프트 로깅
    logger.info("Query: %s", req.text)
    logger.info("Found Documents: %s", [doc["page_content"][:100] + "..." for doc in relevant_docs])

    system_prompt = """
    너는 장애인 복지 제도와 고용 지원에 대해 상담해주는 따뜻한 전문가야.
    사용자는 '장애인 본인'이며, 어떤 지원금이나 도움을 받을 수 있는지 알고 싶어 해.
    사업주나 기관 대상 정책은 제외하고, 개인 장애인이 받을 수 있는 혜택 위주로 설명해줘.
    
    응답 시 다음 규칙을 따라줘:
    1. 사용자가 단순 인사를 하면 간단히 인사로 응답하고, 추가 설명은 하지 마.
    2. 검색된 정책이 있다면, 그 내용을 바탕으로 구체적으로 설명해.
    3. 응답은 항상 친절하고 공감하는 톤을 유지해.
    4. 아래 정책 카드의 내용을 간단히 소개하고, "자세한 내용은 아래 카드를 참고해주세요" 라는 표현을 사용해.
    5. 정책 카드의 내용을 전부 반복하지 말고, 핵심적인 내용만 간단히 언급해.
    """

    user_prompt = f"""
다음 내용을 참고해서 답변해줘:

[정책 내용]
{context}

질문: {req.text}

아래에 정책 카드 {len(cards)}개가 표시될 예정이야. 이 카드들의 내용을 간단히 소개하고, 자세한 내용은 카드를 참고하라고 안내해줘.
"""

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
    )

    return ChatbotResponse(
        answer=completion.choices[0].message.content,
        cards=cards
    )