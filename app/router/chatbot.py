from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.service.embedding import get_embedding
from app.service.mongodb import search_similar_policies, search_chunks_by_keyword
import openai
import os
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv
import traceback

router = APIRouter()

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatMessage(BaseModel):
    text: str
    user_type: str = "장애인"  # 장애인, 가족, 사회복지사
    session_id: Optional[str] = None
    context: Dict = {}

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    intent: str
    next_questions: List[str] = []
    session_id: Optional[str] = None

def analyze_intent(text: str) -> str:
    """사용자의 의도를 분석하는 함수"""
    intent_prompt = f"""
    다음 질문의 의도를 분석해주세요:
    {text}
    
    다음 중 하나로 분류해주세요:
    - 취업_정보: 취업 관련 정보 문의
    - 교육_정보: 교육/훈련 관련 정보 문의
    - 지원금_정보: 지원금/혜택 관련 정보 문의
    - 기관_안내: 관련 기관 안내 요청
    - 기타: 위 카테고리에 해당하지 않는 질문
    """
    
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "의도 분석 전문가입니다."},
            {"role": "user", "content": intent_prompt}
        ]
    )
    
    return completion.choices[0].message.content.strip()

def get_system_prompt(user_type: str) -> str:
    """사용자 유형에 따른 시스템 프롬프트 생성"""
    base_prompt = """
    너는 장애인 취업 지원 전문 상담사입니다.
    다음 원칙을 따라 응답해주세요:
    1. 친절하고 이해하기 쉬운 언어 사용
    2. 단계별로 명확한 안내 제공
    3. 장애인 관련 정책과 서비스에 집중
    4. 필요한 경우 관련 기관 연락처 제공
    5. 사용자의 상황에 맞는 맞춤형 조언
    """
    
    user_specific_prompt = {
        "장애인": "사용자는 장애인 본인입니다. 개인적으로 받을 수 있는 혜택과 지원에 대해 설명해주세요.",
        "가족": "사용자는 장애인의 가족입니다. 가족이 받을 수 있는 지원과 도움에 대해 설명해주세요.",
        "사회복지사": "사용자는 사회복지사입니다. 전문적인 관점에서 장애인 지원 정책과 서비스에 대해 설명해주세요."
    }
    
    return f"{base_prompt}\n{user_specific_prompt.get(user_type, user_specific_prompt['장애인'])}"

def generate_next_questions(intent: str, context: str) -> List[str]:
    """다음 질문 추천 생성"""
    prompt = f"""
    다음 의도와 맥락을 바탕으로 사용자가 물어볼 만한 다음 질문 3가지를 생성해주세요:
    
    의도: {intent}
    맥락: {context}
    
    형식:
    1. 질문1
    2. 질문2
    3. 질문3
    """
    
    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "다음 질문 생성 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    
    questions = completion.choices[0].message.content.strip().split("\n")
    return [q.split(". ")[1] for q in questions if ". " in q]

@router.post("/chatbot/query", response_model=ChatResponse)
async def chatbot_query(req: ChatMessage):
    try:
        # 1. 의도 분석
        intent = analyze_intent(req.text)
        
        # 2. 관련 정보 검색
        embedding = get_embedding(req.text)
        docs = search_similar_policies(embedding, limit=3)
        
        if not docs:
            # 키워드 기반 검색 시도
            docs = search_chunks_by_keyword(req.text, limit=3)
            if not docs:
                return ChatResponse(
                    answer="죄송합니다. 관련된 정보를 찾을 수 없습니다. 다른 방식으로 질문해 주시거나, 한국장애인고용공단(1588-1519)으로 문의해 주시기 바랍니다.",
                    sources=[],
                    intent=intent,
                    next_questions=["장애인 취업 지원 정책에 대해 알고 싶어요.", "장애인 고용장려금은 어떻게 받나요?", "장애인 취업 교육 프로그램이 있나요?"]
                )

        # 3. 컨텍스트 구성
        context = "\n\n---\n\n".join([doc["page_content"] for doc in docs])
        
        # 4. 시스템 프롬프트 생성
        system_prompt = get_system_prompt(req.user_type)
        
        # 5. 응답 생성
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
                [참고 정보]
                {context}
                
                [사용자 질문]
                {req.text}
                """}
            ]
        )
        
        # 6. 다음 질문 생성
        next_questions = generate_next_questions(intent, context)
        
        return ChatResponse(
            answer=completion.choices[0].message.content,
            sources=[doc["metadata"]["url"] for doc in docs],
            intent=intent,
            next_questions=next_questions,
            session_id=req.session_id
        )
        
    except Exception as e:
        print("==== [chatbot.py] 에러 발생 ====")
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))