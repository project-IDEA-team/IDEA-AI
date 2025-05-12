from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DialogueState(str, Enum):
    """대화 상태를 나타내는 열거형"""
    START = "start"
    AWAITING_SLOTS = "awaiting_slots"
    RESULTS_SHOWN = "results_shown"
    ERROR = "error"
    CLARIFYING = "clarifying"

class ButtonType(str, Enum):
    """버튼 유형을 나타내는 열거형"""
    LINK = "link"
    TEL = "tel"
    EMAIL = "email"
    SHARE = "share"

class CardButton(BaseModel):
    """카드의 버튼 모델"""
    type: ButtonType = Field(..., description="버튼 유형")
    label: str = Field(..., description="버튼 레이블")
    value: str = Field(..., description="버튼 값 (URL, 전화번호, 이메일 등)")

class CardSource(BaseModel):
    """카드의 출처 정보 모델"""
    url: Optional[str] = Field(None, description="출처 URL")
    name: Optional[str] = Field(None, description="출처 이름")
    phone: Optional[str] = Field(None, description="문의 전화번호")
    email: Optional[str] = Field(None, description="문의 이메일")

class Card(BaseModel):
    """정보 카드 기본 모델"""
    id: str = Field(..., description="카드 고유 ID")
    title: str = Field(..., description="카드 제목")
    subtitle: Optional[str] = Field(None, description="카드 부제목")
    summary: str = Field(..., description="카드 요약")
    type: str = Field(..., description="카드 유형 (policy, employment, welfare, startup, medical, education, counseling)")
    details: str = Field(..., description="카드 상세 내용")
    icon: Optional[str] = Field(None, description="카드 아이콘")
    source: Optional[CardSource] = Field(None, description="카드 출처 정보")
    buttons: Optional[List[CardButton]] = Field(None, description="카드 버튼 목록")
    tags: Optional[List[str]] = Field(None, description="카드 태그 목록")

class ExpertCard(Card):
    """전문가 선택 카드 모델"""
    expert_type: str = Field(..., description="전문가 유형")
    description: str = Field(..., description="전문가 설명")

class ChatbotResponse(BaseModel):
    """챗봇 응답 모델"""
    answer: str = Field(..., description="챗봇 응답 텍스트")
    state: DialogueState = Field(..., description="현재 대화 상태")
    intent: Optional[str] = Field(None, description="인식된 사용자 의도")
    slots: Optional[Dict[str, Any]] = Field(None, description="수집된 슬롯 정보")
    needs_more_info: bool = Field(False, description="추가 정보 필요 여부")
    cards: Optional[List[Card]] = Field(None, description="관련 정보 카드 목록")
    action_cards: Optional[List[ExpertCard]] = Field(None, description="전문가 선택 카드 목록")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="대화 이력") 