"""
LLM 에이전트 클래스
챗봇 응답을 처리합니다. (리팩토링: 공공데이터 API 호출 코드 제거)
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

from app.service.openai_client import get_client

logger = logging.getLogger(__name__)

class LLMAgent:
    """
    LLM 에이전트 클래스
    OpenAI를 사용하여 사용자 쿼리에 응답합니다.
    """
    
    def __init__(self, model_name="gpt-4.1-mini"):
        """
        초기화
        
        Args:
            model_name: 사용할 OpenAI 모델명
        """
        self.client = get_client()
        self.model_name = model_name
        self.system_prompt = """
        당신은 장애인 복지 정보를 제공하는 AI 챗봇입니다.
        사용자의 질문에 대해 유용한 정보를 제공하세요.
        
        응답 시 다음 규칙을 따르세요:
        1. 항상 공감적이고 친절한 어조로 응답하세요.
        2. 정보를 명확하고 구조화된 형태로 제공하세요.
        3. 전문 용어는 가능한 쉬운 표현으로 설명하세요.
        4. 추가 도움이 필요한 경우 관련 자원이나 연락처를 제공하세요.
        """
    
    async def process_query(self, query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        사용자 쿼리를 처리하여 응답을 생성합니다.
        
        Args:
            query: 사용자 질문
            conversation_history: 이전 대화 내용
            
        Returns:
            응답 텍스트
        """
        try:
            # 대화 이력 처리
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if conversation_history:
                # 최근 5개 메시지만 포함
                recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
                for msg in recent_history:
                    if msg.get("role") and msg.get("content"):
                        messages.append({"role": msg["role"], "content": msg["content"]})
            
            # 현재 쿼리 추가
            messages.append({"role": "user", "content": query})
            
            # LLM에 요청 전송
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            
            # 응답 처리
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"쿼리 처리 중 오류 발생: {e}")
            return f"죄송합니다. 요청을 처리하는 중 오류가 발생했습니다: {str(e)}"
    
    async def search_with_api_tools(self, query: str, keywords: List[str], expert_type: str = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        사용자 쿼리에 대해 검색 후 응답과 정보 카드를 반환합니다.
        API 호출 대신 기본 데이터를 반환합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            expert_type: 전문가 유형 (선택사항)
            
        Returns:
            검색 결과 기반 응답과 정보 카드 목록
        """
        # 키워드 처리 (불필요한 처리 간소화)
        processed_keywords = []
        if keywords and isinstance(keywords, list):
            for item in keywords:
                if isinstance(item, str):
                    processed_keywords.append(item)
                elif isinstance(item, dict) and 'content' in item:
                    text = item['content']
                    words = text.split()
                    for word in words:
                        if len(word) > 1 and word not in processed_keywords:
                            processed_keywords.append(word)
            
            if len(processed_keywords) > 10:
                processed_keywords = processed_keywords[:10]
        
        if not processed_keywords:
            processed_keywords = ["장애인", "정보", "지원"]
            
        logger.info(f"처리된 키워드: {processed_keywords}")
        
        # 기본 정보 카드 데이터
        default_cards = []
        
        # 전문가 유형에 따른 기본 데이터 제공
        if expert_type == "취업" or expert_type == "장애인 취업":
            default_cards = [{
                "id": "job-1",
                "title": "장애인 취업 지원 제도",
                "subtitle": "취업 지원",
                "summary": "장애인을 위한 다양한 취업 지원 제도 안내",
                "type": "employment",
                "details": (
                    "장애인 취업을 위한 다양한 지원 제도가 있습니다:\n\n"
                    "1. 장애인 고용 장려금\n"
                    "2. 근로지원인 서비스\n"
                    "3. 보조공학기기 지원\n"
                    "4. 취업 후 적응 지도\n"
                    "5. 장애인 표준사업장 지원\n\n"
                    "가까운 한국장애인고용공단 지사나 고용센터에서 상담받을 수 있습니다."
                ),
                "source": {
                    "url": "https://www.worktogether.or.kr/main.do",
                    "name": "장애인고용포털",
                    "phone": "1588-1519"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.worktogether.or.kr/main.do"},
                    {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
                ]
            }]
        elif expert_type == "복지" or expert_type == "장애인 복지":
            default_cards = [{
                "id": "welfare-1",
                "title": "장애인 복지 서비스",
                "subtitle": "복지 서비스",
                "summary": "장애인을 위한 주요 복지 서비스 안내",
                "type": "welfare",
                "details": (
                    "장애인을 위한 주요 복지 서비스:\n\n"
                    "1. 장애인연금 및 장애수당\n"
                    "2. 장애인 활동지원 서비스\n"
                    "3. 장애인 보조기기 지원\n"
                    "4. 발달장애인 주간활동 및 방과후활동 서비스\n"
                    "5. 장애인 주거 지원\n\n"
                    "신청 방법: 주소지 관할 읍·면·동 주민센터 방문 신청"
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.bokjiro.go.kr"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
        elif expert_type == "정책" or expert_type == "장애인 정책":
            default_cards = [{
                "id": "policy-1",
                "title": "장애인 정책 정보",
                "subtitle": "정책 정보",
                "summary": "장애인 관련 주요 정책 및 제도 안내",
                "type": "policy",
                "details": (
                    "장애인 관련 주요 정책 및 제도:\n\n"
                    "1. 장애인 등록 제도\n"
                    "2. 장애인 차별금지 및 권리구제 제도\n"
                    "3. 장애등급제 폐지 및 수요자 중심 지원 체계\n"
                    "4. 장애인 자립생활 지원 정책\n"
                    "5. 장애인 인권 보장 제도\n\n"
                    "관련 문의: 보건복지상담센터(129) 또는 장애인권익옹호기관"
                ),
                "source": {
                    "url": "https://www.mohw.go.kr",
                    "name": "보건복지부",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.mohw.go.kr"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
        else:
            # 기본 정보 카드
            default_cards = [{
                "id": "general-info",
                "title": "장애인 지원 정보",
                "subtitle": "종합 정보",
                "summary": "장애인을 위한 다양한 지원 제도 안내",
                "type": "general",
                "details": (
                    "장애인을 위한 다양한 지원 제도가 있습니다:\n\n"
                    "1. 장애인 등록 및 심사 제도\n"
                    "2. 경제적 지원 (연금, 수당, 감면 혜택 등)\n"
                    "3. 일상생활 지원 (활동지원, 보조기기 등)\n"
                    "4. 고용 및 취업 지원\n"
                    "5. 교육 및 문화생활 지원\n\n"
                    "자세한 내용은 주소지 관할 읍·면·동 주민센터나 보건복지상담센터(129)에 문의하세요."
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.bokjiro.go.kr"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
        
        # 시스템 프롬프트 생성
        keyword_strings = [k for k in processed_keywords if isinstance(k, str)]
        system_prompt = f"""
        당신은 장애인 관련 정보를 제공하는 AI 도우미입니다.
        
        1. 사용자 질문: "{query}"
        2. 관련 키워드: {', '.join(keyword_strings) if keyword_strings else "장애인 정보"}
        
        제공된 키워드와 질문을 바탕으로 사용자에게 도움이 될 정보를 친절하게 설명해주세요.
        항상 공감적이고 정확한 정보를 제공하도록 노력하세요.
        """
        
        # LLM 응답 생성
        messages = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "user", "content": query})
        
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        response_text = response.choices[0].message.content
        
        return response_text, default_cards
    
    async def process_user_message(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        사용자 메시지를 처리하고 응답을 생성합니다.
        
        Args:
            user_message: 사용자 메시지
            conversation_history: 대화 이력
            
        Returns:
            챗봇 응답
        """
        return await self.process_query(user_message, conversation_history) 