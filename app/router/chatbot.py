from fastapi import APIRouter, HTTPException, Request, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.service.dialogue_manager import DialogueManager
from app.models.response import ChatbotResponse, Card, ExpertCard, DialogueState
from app.service.agents.general_chatbot import GeneralChatbot
from app.service.agents.supervisor import SupervisorAgent
from app.models.expert_type import ExpertType, UserType
from app.service.analyzer.benefit_analysis import analyze_and_store
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_type: UserType
    session_state: Optional[Dict[str, Any]] = None

class ExpertQueryRequest(BaseModel):
    text: str
    expert_type: ExpertType
    user_type: UserType
    session_state: Optional[Dict[str, Any]] = None

class ConversationRequest(BaseModel):
    messages: List[Dict[str, Any]]
    expert_type: Optional[str] = None

# 의존성 주입을 위한 함수
def get_general_chatbot():
    return GeneralChatbot()

def get_supervisor_agent():
    return SupervisorAgent()

def get_dialogue_manager():
    return DialogueManager()

@router.post("/chat/start", response_model=ChatbotResponse)
async def start_chat(user_type: UserType = Query(..., description="사용자 유형 (disabled: 장애인, company: 기업)")):
    """초기 대화를 시작합니다."""
    if user_type == UserType.DISABLED:
        expert_cards = [
            ExpertCard(
                id="policy",
                title="정책 전문가",
                expert_type=ExpertType.POLICY,
                description="의료, 복지, 취업 관련 정부 정책 정보 제공",
                icon="📜",
                type="expert",
                summary="장애인 정책 정보 제공",
                details="장애인 복지 정책, 의료 지원, 취업 지원 등에 대한 종합적인 정보를 제공합니다."
            ),
            ExpertCard(
                id="employment",
                title="취업/창업 전문가",
                expert_type=ExpertType.EMPLOYMENT,
                description="취업 정보, 직업 교육, 창업 지원 안내",
                icon="💼",
                type="expert",
                summary="장애인 취업/창업 정보 제공"
            )
        ]
        welcome_message = "안녕하세요! 장애인 복지 정보 챗봇입니다. 어떤 정보를 찾으시나요?"
    else:
        expert_cards = [
            ExpertCard(
                id="company_policy",
                title="기업 정책 전문가",
                expert_type=ExpertType.COMPANY_POLICY,
                description="장애인 고용 관련 법률 및 지원금 안내",
                icon="⚖️",
                type="expert",
                summary="기업 정책 정보 제공",
                details="장애인 고용 관련 법률 및 지원금에 대한 상세 안내를 제공합니다. 의무고용률, 고용장려금, 시설장비 지원금 등 기업이 알아야 할 핵심 정보를 안내해드립니다."
            ),
            ExpertCard(
                id="recruitment",
                title="구인/인재 전문가",
                expert_type=ExpertType.RECRUITMENT,
                description="장애인 구직자 정보 및 채용 절차 안내",
                icon="🤝",
                type="expert",
                summary="구인/구직 정보 제공",
                details="장애인 구직자 정보 검색 및 매칭, 채용 절차 안내, 정부 지원 제도 등 채용과 관련된 모든 정보를 제공합니다."
            )
        ]
        welcome_message = "안녕하세요! 기업을 위한 장애인 고용 지원 챗봇입니다. 어떤 정보를 찾으시나요?"
    
    return ChatbotResponse(
        answer=welcome_message,
        state=DialogueState.START,
        needs_more_info=False,
        action_cards=expert_cards
    )

@router.post("/chat/conversation", response_model=ChatbotResponse)
async def process_conversation(
    req: ChatRequest,
    dialogue_manager: DialogueManager = Depends(get_dialogue_manager),
    general_chatbot: GeneralChatbot = Depends(get_general_chatbot)
):
    """사용자 메시지를 처리하고 응답을 생성합니다."""
    try:
        current_message = req.messages[-1].content if req.messages else ""
        session_state = req.session_state or {}
        
        # ChatMessage 객체를 딕셔너리로 변환
        messages_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in req.messages
        ]
        
        # 대화 관리자를 통한 메시지 처리
        response = await dialogue_manager.process_message(
            text=current_message,
            session_state=session_state,
            user_type=req.user_type
        )
        
        # 일반 챗봇을 통한 응답 가공
        friendly_response = await general_chatbot.create_user_friendly_response(
            expert_response=response,
            conversation=messages_dict,  # 변환된 딕셔너리 리스트 사용
            user_type=req.user_type
        )
        
        # 응답 구성
        chatbot_response = ChatbotResponse(
            answer=friendly_response["answer"],
            state=DialogueState(response.get("state", DialogueState.ERROR)),
            intent=response.get("intent"),
            slots=response.get("slots"),
            needs_more_info=response.get("needs_more_info", False),
            cards=friendly_response.get("cards"),
            action_cards=response.get("action_cards"),
            conversation_history=messages_dict  # 변환된 딕셔너리 리스트 사용
        )
        
        return chatbot_response
        
    except Exception as e:
        logger.exception("Error processing conversation")
        return ChatbotResponse(
            answer="죄송합니다. 요청을 처리하는 중 오류가 발생했습니다.",
            state=DialogueState.ERROR,
            needs_more_info=False
        )

@router.post("/chat/expert", response_model=ChatbotResponse)
async def chat_expert_query(
    req: ExpertQueryRequest,
    dialogue_manager: DialogueManager = Depends(get_dialogue_manager),
    general_chatbot: GeneralChatbot = Depends(get_general_chatbot)
):
    """전문가 AI와의 대화를 처리합니다."""
    try:
        session_state = req.session_state or {}
        session_state["expert_type"] = req.expert_type
        
        # 대화 관리자를 통한 메시지 처리
        response = await dialogue_manager.process_message(
            text=req.text,
            session_state=session_state,
            user_type=req.user_type
        )
        
        # 일반 챗봇을 통한 응답 가공
        friendly_response = await general_chatbot.create_user_friendly_response(
            expert_response=response,
            conversation=[{"role": "user", "content": req.text}],
            user_type=req.user_type
        )
        
        chatbot_response = ChatbotResponse(
            answer=friendly_response["answer"],
            state=DialogueState(response.get("state", DialogueState.ERROR)),
            intent=response.get("intent"),
            slots=response.get("slots"),
            needs_more_info=response.get("needs_more_info", False),
            cards=friendly_response.get("cards"),
            action_cards=response.get("action_cards")
        )
        
        return chatbot_response
        
    except Exception as e:
        logger.exception("Error processing expert query")
        return ChatbotResponse(
            answer="죄송합니다. 전문가 응답을 처리하는 중 오류가 발생했습니다.",
            state=DialogueState.ERROR,
            needs_more_info=False
        )

@router.post("/analyze/benefits")
async def analyze_endpoint(user_info: dict, job_info: dict):
    result = await analyze_and_store(user_info, job_info)
    return result or {"error": "분석 실패"}