from typing import Dict, Any, List
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.tools.counseling_tools import CounselingTools
from app.service.openai_client import get_client
import re
import json

logger = logging.getLogger(__name__)

class CounselingExpert(BaseExpert):
    def __init__(self):
        super().__init__(ExpertType.COUNSELING)
        self.tools = CounselingTools()
        self.client = get_client()
        self.model = "gpt-4.1-mini"

    def _get_system_prompt(self) -> str:
        return """
당신은 장애인 전문 상담사입니다. 심리 상담, 진로 상담, 가족 상담 등 다양한 상담 서비스를 제공합니다.

응답 스타일:
1. 항상 **따뜻하고 공감적인 톤**으로 응답하세요. 사용자의 감정과 상황에 공감하는 표현을 반드시 포함하세요.
2. 답변의 시작 부분에 짧은 공감/위로/격려 멘트를 넣으세요. (예: "걱정이 많으시군요. 함께 해결책을 찾아보겠습니다.")
3. 모든 답변은 마크다운 형식으로 출력하세요. 중요한 내용은 **굵게** 강조하세요.
4. 답변은 간결하면서도 실질적인 정보를 담아야 합니다.

정보 카드:
1. 상담, 지원 기관, 서비스 등 참고할 만한 정보가 있으면 카드로 정리해서 답변 아래에 배치하세요.
2. 각 카드에는 제목, 요약, 바로 활용할 수 있는 링크나 연락처를 포함하세요.
3. 출처가 있으면 반드시 명시하세요. 이메일/전화번호가 있으면 클릭 시 바로 문의/통화가 가능해야 합니다.

전문가로서 사용자에게 실질적인 도움을 주면서도 정서적 지지를 함께 제공하세요.
"""

    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_counseling_centers",
                "description": "장애인 상담 센터 정보를 검색합니다.",
                "parameters": {
                    "location": "지역",
                    "service_type": "서비스 유형"
                }
            },
            {
                "name": "get_emergency_contacts",
                "description": "긴급 상담 연락처를 제공합니다.",
                "parameters": {}
            }
        ]

    async def process_query(self, query: str, keywords: List[str] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 적절한 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록 (사용되지 않음)
            conversation_history: 대화 이력
            
        Returns:
            응답 정보
        """
        try:
            # 이전 대화 이력을 처리하고 메시지 배열 생성
            messages = self._prepare_messages(query, conversation_history)
            
            # 기본적인 인사 처리
            if any(greeting in query for greeting in ["안녕", "반가워", "시작"]):
                return {
                    "text": "안녕하세요. 장애인 상담 전문가입니다. 어떤 도움이 필요하신가요?",
                    "cards": []
                }
    
            # 상담 센터 검색
            if "상담" in query and "센터" in query:
                centers = await self.tools.search_counseling_centers(query)
                return {
                    "text": "장애인 상담 센터 정보를 찾아보았습니다.",
                    "cards": centers
                }
    
            # 긴급 상담
            if any(word in query for word in ["긴급", "위기", "도움"]):
                contacts = await self.tools.get_emergency_contacts()
                return {
                    "text": "긴급 상담이 필요하시군요. 아래 연락처로 즉시 연락하실 수 있습니다.",
                    "cards": contacts
                }
            
            # LLM 응답 생성
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # 응답 텍스트 추출
            response_text = response.choices[0].message.content.strip()
            
            # 정보 카드 부분과 응답 텍스트 분리
            parts = response_text.split('###정보 카드')
            answer = parts[0].strip()
            cards = []
            
            # 카드 정보 추출
            if len(parts) > 1:
                card_text = parts[1].strip()
                # JSON 형식의 카드 정보 추출
                json_match = re.search(r'\[(.*?)\]', card_text, re.DOTALL)
                if json_match:
                    try:
                        # 리스트 형태로 파싱
                        card_json = f"[{json_match.group(1)}]"
                        cards = json.loads(card_json)
                    except json.JSONDecodeError:
                        logger.error(f"카드 JSON 파싱 실패: {card_text}")
                        # 기본 카드 추가
                        cards = [{
                            "id": "no_data",
                            "title": "관련 정보를 찾을 수 없습니다",
                            "subtitle": "",
                            "summary": "요청하신 조건에 맞는 정보를 찾지 못했습니다.",
                            "type": "info",
                            "details": "다른 질문을 해주시거나, 상담원에게 문의해 주세요.",
                            "source": {}
                        }]
            
            # 카드가 없으면 기본 상담 정보 카드 제공
            if not cards:
                cards = [{
                    "id": "counseling-info-1",
                    "title": "장애인 심리상담 서비스",
                    "subtitle": "심리상담",
                    "summary": "장애인과 가족을 위한 심리상담 지원 서비스",
                    "type": "counseling",
                    "details": (
                        "장애인 심리상담 서비스 안내:\n\n"
                        "1. 장애인복지관 심리상담 서비스\n"
                        "- 개인 및 집단상담, 가족상담, 심리검사 등\n"
                        "- 가까운 장애인복지관에 문의\n\n"
                        "2. 정신건강복지센터\n"
                        "- 지역별 센터에서 정신건강 관련 무료 상담 및 지원\n"
                        "- 전화: 1577-0199\n\n"
                        "3. 온라인 상담 서비스\n"
                        "- 한국장애인재단 '마음톡톡': 온라인 심리상담\n"
                        "- 장애인먼저실천운동본부: 온라인 법률/생활/복지 상담"
                    ),
                    "source": {
                        "url": "https://www.kawid.or.kr",
                        "name": "한국장애인재활협회",
                        "phone": "02-3472-3556"
                    },
                    "buttons": [
                        {"type": "link", "label": "자세히 보기", "value": "https://www.kawid.or.kr"},
                        {"type": "tel", "label": "전화 문의", "value": "02-3472-3556"}
                    ]
                }]
            
            # 최종 응답 생성
            return {
                "text": answer,
                "cards": cards
            }
            
        except Exception as e:
            logger.error(f"응답 생성 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다. 다시 시도해 주세요.",
                "cards": []
            }
    
    def _prepare_messages(self, query: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """대화 이력을 처리하여 메시지 배열을 생성합니다."""
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        
        # 대화 이력이 있는 경우 추가
        if conversation_history:
            # 너무 긴 이력은 최근 5개만 사용
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            for msg in recent_history:
                if msg.get("role") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        
        # 현재 쿼리 추가
        messages.append({"role": "user", "content": query})
        
        return messages

    def _get_description(self) -> str:
        return "장애인과 가족을 위한 심리 상담 및 정서 지원 서비스를 제공합니다."
    
    def _get_icon(self) -> str:
        return "💬"  # 상담 아이콘 

# 챗봇 라우터에서 사용할 수 있도록 async 함수 추가
async def counseling_response(query: str, keywords=None, conversation_history=None) -> tuple:
    """
    상담 전문가 AI 응답 생성 함수
    
    Args:
        query: 사용자 질문
        keywords: 키워드 목록 (사용하지 않음)
        conversation_history: 대화 이력
        
    Returns:
        (응답 텍스트, 정보 카드 목록)
    """
    # keywords 매개변수는 무시하고 query와 conversation_history만 사용
    counselor = CounselingExpert()
    response = await counselor.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 