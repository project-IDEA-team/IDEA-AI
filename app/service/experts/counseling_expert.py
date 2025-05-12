from typing import Dict, Any, List
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.tools.counseling_tools import CounselingTools
from app.service.openai_client import get_client
import re
import json
from app.service.experts.common_form.example_cards import COUNSELING_CARD_TEMPLATE

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

모든 정보 카드는 반드시 아래와 같은 JSON 형식으로 만들어 주세요.
{
  "id": "string",
  "title": "string",
  "subtitle": "string",
  "summary": "string",
  "type": "string",
  "details": "string",
  "source": {
    "url": "string",
    "name": "string",
    "phone": "string"
  },
  "buttons": [
    {"type": "link", "label": "string", "value": "string"},
    {"type": "tel", "label": "string", "value": "string"}
  ]
}

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
            },
            {
                "type": "function",
                "function": {
                    "name": "search_counseling_services",
                    "description": "장애인 상담 서비스 정보를 검색합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "검색 키워드 목록"
                            },
                            "service_type": {
                                "type": "string",
                                "description": "상담 서비스 유형"
                            },
                            "disability_type": {
                                "type": "string",
                                "description": "장애 유형"
                            },
                            "region": {
                                "type": "string",
                                "description": "지역 정보"
                            }
                        },
                        "required": ["keywords"]
                    }
                }
            }
        ]

    async def search_counseling_services(self, keywords: List[str], service_type: str = None, disability_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        """
        상담 서비스 정보를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            service_type: 서비스 유형
            disability_type: 장애 유형
            region: 지역 정보
            
        Returns:
            상담 서비스 정보 카드 목록
        """
        try:
            # 실제 DB/API 검색 로직 구현 필요
            cards = []
            
            # 검색 결과 없으면 fallback 카드
            if not cards:
                cards = [{
                    "id": "counseling-general",
                    "title": "장애인 상담 서비스 안내",
                    "subtitle": "상담 정보",
                    "summary": "장애인을 위한 다양한 상담 서비스 종합 안내",
                    "type": "counseling",
                    "details": "검색 결과가 없습니다. 가까운 장애인복지관이나 상담센터에 문의하세요.",
                    "source": {
                        "url": "https://www.129.go.kr",
                        "name": "보건복지상담센터",
                        "phone": "129"
                    },
                    "buttons": [
                        {"type": "link", "label": "복지포털 홈페이지", "value": "https://www.129.go.kr"},
                        {"type": "tel", "label": "상담 문의", "value": "129"}
                    ]
                }]
            return cards
            
        except Exception as e:
            logger.error(f"상담 서비스 검색 중 오류 발생: {str(e)}")
            return [COUNSELING_CARD_TEMPLATE]

    async def _search_counseling_info(self, query: str, keywords: List[str]) -> Dict[str, Any]:
        """
        상담 정보를 검색하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 상담 정보 카드 검색
            counseling_cards = await self.search_counseling_services(keywords)
            
            # 각 카드의 형식 수정
            formatted_cards = []
            for card in counseling_cards:
                # 카드 제목은 상담 서비스명 사용
                card["title"] = card.get("title", "상담 정보")
                
                # 요약은 한 줄로 제한
                summary = card.get("summary", "")
                if len(summary) > 50:  # 요약은 50자로 제한
                    summary = summary[:47] + "..."
                card["summary"] = summary
                
                # 버튼에 실제 링크 추가
                if "source" in card and "url" in card["source"]:
                    card["buttons"] = [
                        {
                            "type": "link",
                            "label": "자세히 보기",
                            "value": card["source"]["url"]
                        }
                    ]
                    # 전화번호가 있으면 전화 버튼 추가
                    if "phone" in card["source"] and card["source"]["phone"]:
                        card["buttons"].append({
                            "type": "tel",
                            "label": "전화 상담",
                            "value": card["source"]["phone"]
                        })
                
                formatted_cards.append(card)
            
            # 응답 텍스트 생성
            response_text = "안녕하세요! 문의하신 상담 정보를 알려드리겠습니다.\n\n"
            
            # 각 카드의 핵심 정보를 텍스트에 추가
            for card in formatted_cards:
                response_text += f"• {card['title']}\n"
                response_text += f"{card['summary']}\n"
                if "source" in card and "phone" in card["source"]:
                    response_text += f"문의: {card['source']['name']} ({card['source']['phone']})\n"
                response_text += "\n"
            
            return {
                "text": response_text.strip(),
                "cards": formatted_cards
            }
            
        except Exception as e:
            logger.error(f"상담 정보 검색 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 상담 정보를 검색하는 중에 문제가 발생했습니다.",
                "cards": [COUNSELING_CARD_TEMPLATE]
            }

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
            # 검색 키워드 추출
            search_keywords = self._extract_search_keywords(query, keywords)
            logger.debug(f"추출된 검색 키워드: {search_keywords}")
            
            # 상담 정보 검색
            response = await self._search_counseling_info(query, search_keywords)
            
            # 응답 검증 및 수정
            validated_response = self.validate_response(response)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"응답 생성 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다. 다시 시도해 주세요.",
                "cards": [{**COUNSELING_CARD_TEMPLATE, "details": "시스템 오류로 정보를 불러올 수 없습니다."}]
            }

    def _extract_search_keywords(self, query: str, keywords: List[str] = None) -> List[str]:
        """
        검색에 사용할 키워드를 추출합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 제공한 키워드 목록
            
        Returns:
            검색 키워드 목록
        """
        try:
            # 1. 기본 키워드 (장애인, 상담)
            base_keywords = ["장애인", "상담"]
            
            # 2. 슈퍼바이저가 제공한 키워드가 있으면 사용
            if keywords and isinstance(keywords, list):
                valid_keywords = [kw for kw in keywords if isinstance(kw, str)]
                if valid_keywords:
                    return base_keywords + valid_keywords[:3]  # 최대 3개 키워드만 사용
            
            # 3. 쿼리에서 직접 키워드 추출
            query_keywords = []
            
            # 주요 키워드 패턴
            key_patterns = [
                r"장애인\s+(\w+)",  # "장애인 상담" -> "상담"
                r"(\w+)\s+상담",    # "심리 상담" -> "심리"
                r"(\w+)\s+치료",    # "우울증 치료" -> "우울증"
                r"(\w+)\s+문제",    # "가족 문제" -> "가족"
                r"(\w+)\s+적응"     # "사회 적응" -> "사회"
            ]
            
            import re
            for pattern in key_patterns:
                matches = re.findall(pattern, query)
                query_keywords.extend(matches)
            
            # 중복 제거 및 정제
            query_keywords = list(set(query_keywords))
            query_keywords = [kw.strip() for kw in query_keywords if len(kw.strip()) > 1]
            
            # 최종 키워드 조합 (기본 키워드 + 쿼리 키워드)
            final_keywords = base_keywords + query_keywords[:3]  # 최대 3개 키워드만 사용
            
            logger.info(f"최종 검색 키워드: {final_keywords}")
            return final_keywords
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류 발생: {str(e)}")
            return ["장애인", "상담"]  # 오류 발생 시 기본 키워드만 반환

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

    def _format_card(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """카드 데이터를 공통 포맷으로 변환"""
        return {
            "id": data.get("id", COUNSELING_CARD_TEMPLATE["id"]),
            "title": data.get("title", COUNSELING_CARD_TEMPLATE["title"]),
            "subtitle": data.get("subtitle", COUNSELING_CARD_TEMPLATE["subtitle"]),
            "summary": data.get("summary", COUNSELING_CARD_TEMPLATE["summary"]),
            "type": data.get("type", COUNSELING_CARD_TEMPLATE["type"]),
            "details": data.get("details", COUNSELING_CARD_TEMPLATE["details"]),
            "source": data.get("source", COUNSELING_CARD_TEMPLATE["source"]),
            "buttons": data.get("buttons", COUNSELING_CARD_TEMPLATE["buttons"])
        }

    def _get_description(self) -> str:
        return "장애인과 가족을 위한 심리 상담 및 정서 지원 서비스를 제공합니다."
    
    def _get_icon(self) -> str:
        return "💬"  # 상담 아이콘 

# 챗봇 라우터에서 사용할 수 있도록 async 함수 추가
async def counseling_response(query: str, keywords: List[str] = None, conversation_history: List[Dict[str, str]] = None) -> tuple:
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