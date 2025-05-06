from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PolicyCardButton(BaseModel):
    """정책 카드의 버튼 모델"""
    type: str = Field(..., description="버튼 유형 (link, tel, email, share)")
    label: str = Field(..., description="버튼 레이블")
    value: str = Field(..., description="버튼 값 (URL, 전화번호, 이메일 등)")

class PolicyCardSource(BaseModel):
    """정책 카드의 출처 모델"""
    url: Optional[str] = Field(None, description="출처 URL")
    name: Optional[str] = Field(None, description="출처 이름")
    email: Optional[str] = Field(None, description="문의 이메일")
    phone: Optional[str] = Field(None, description="문의 전화번호")

class PolicyCard(BaseModel):
    """정책 카드 모델"""
    id: str = Field(..., description="카드 고유 ID")
    title: str = Field(..., description="카드 제목")
    subtitle: Optional[str] = Field(None, description="카드 부제목")
    summary: str = Field(..., description="카드 요약")
    type: str = Field(..., description="카드 유형 (policy, employment, welfare, startup, medical, education, counseling)")
    details: str = Field(..., description="카드 상세 내용")
    imageUrl: Optional[str] = Field(None, description="카드 이미지 URL")
    source: Optional[PolicyCardSource] = Field(None, description="카드 출처 정보")
    buttons: Optional[List[PolicyCardButton]] = Field(None, description="카드 버튼 목록")

class ExpertCard(BaseModel):
    """전문가 카드 모델"""
    id: str = Field(..., description="카드 고유 ID")
    title: str = Field(..., description="전문가 이름")
    expert_type: str = Field(..., description="전문가 유형")
    description: str = Field(..., description="전문가 설명")
    icon: Optional[str] = Field(None, description="전문가 아이콘")

class ChatbotResponse(BaseModel):
    """챗봇 응답 모델"""
    answer: str = Field(..., description="챗봇 응답 텍스트")
    cards: Optional[List[PolicyCard]] = Field(None, description="관련 정책 카드 목록")
    action_cards: Optional[List[ExpertCard]] = Field(None, description="전문가 선택 카드 목록") 