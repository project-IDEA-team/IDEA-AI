from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.service.experts import get_expert_response
from app.service.agents.general_chatbot import GeneralChatbot
from app.service.agents.supervisor import SupervisorAgent

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ExpertQueryRequest(BaseModel):
    text: str
    expert_type: str

class ConversationRequest(BaseModel):
    messages: List[Dict[str, Any]]
    expert_type: Optional[str] = None

# 의존성 주입을 위한 함수
def get_general_chatbot():
    return GeneralChatbot()

def get_supervisor_agent():
    return SupervisorAgent()

@router.post("/chat/start")
async def start_chat():
    expert_cards = [
        {
            "id": "policy",
            "title": "정책 전문가",
            "expert_type": "장애인 정책",
            "description": "정부, 지자체의 장애인 관련 법률 및 제도 안내",
            "icon": "📜"
        },
        {
            "id": "employment",
            "title": "취업 전문가",
            "expert_type": "장애인 취업",
            "description": "공공기관 및 민간기업 취업 정보 제공",
            "icon": "💼"
        },
        {
            "id": "welfare",
            "title": "복지 전문가",
            "expert_type": "장애인 복지",
            "description": "장애인 복지 서비스 및 혜택 안내",
            "icon": "🏥"
        },
        {
            "id": "startup",
            "title": "창업 전문가",
            "expert_type": "장애인 창업",
            "description": "장애인 창업 지원 제도 및 프로그램 안내",
            "icon": "🚀"
        },
        {
            "id": "medical",
            "title": "의료 전문가",
            "expert_type": "장애인 의료",
            "description": "장애 유형별 진료 및 의료 지원 정보",
            "icon": "⚕️"
        },
        {
            "id": "education",
            "title": "교육 전문가",
            "expert_type": "장애인 교육",
            "description": "장애인 교육 프로그램 및 지원 제도 안내",
            "icon": "📚"
        },
        {
            "id": "counseling",
            "title": "상담 전문가",
            "expert_type": "전문 상담",
            "description": "장애인 심리 상담 및 가족 상담 프로그램",
            "icon": "💬"
        }
    ]
    return {
        "answer": "안녕하세요! 장애인 복지 전문 챗봇입니다. 원하시는 서비스를 선택해주세요.",
        "action_cards": expert_cards
    }

@router.post("/chat/expert")
async def chat_expert_query(req: ExpertQueryRequest):
    try:
        answer, cards = await get_expert_response(req.text, req.expert_type)
        return {"answer": answer, "cards": cards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/conversation")
async def process_conversation(
    req: ConversationRequest,
    general_chatbot: GeneralChatbot = Depends(get_general_chatbot),
    supervisor_agent: SupervisorAgent = Depends(get_supervisor_agent)
):
    try:
        # 현재 메시지 추출
        latest_message = req.messages[-1]["content"] if req.messages else ""
        
        # 전문가 유형이 지정된 경우
        if req.expert_type:
            expert_response = await get_expert_response(
                latest_message,
                req.expert_type,
                req.messages  # 대화 이력 전달
            )
            
            # 사용자 친화적 응답 생성
            user_friendly_response = await general_chatbot.create_user_friendly_response(
                {"answer": expert_response[0], "cards": expert_response[1]},
                req.messages
            )
            
            return {
                "answer": user_friendly_response,
                "cards": expert_response[1]
            }
        
        # 전문가 유형이 지정되지 않은 경우 (일반 대화)
        # 일반 챗봇 처리
        general_response = await general_chatbot.process_initial_query(latest_message)
        
        # 슈퍼바이저 분석
        expert_type, keywords = await supervisor_agent.analyze_conversation(req.messages)
        
        # 적합한 전문가 응답 생성 (대화 이력 전달)
        expert_response = await get_expert_response(
            latest_message, 
            expert_type.value,
            req.messages
        )
        
        # 응답 종합
        combined_response = await supervisor_agent.consolidate_responses([
            {"answer": general_response["initial_response"], "cards": []},
            {"answer": expert_response[0], "cards": expert_response[1]}
        ])
        
        return combined_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))