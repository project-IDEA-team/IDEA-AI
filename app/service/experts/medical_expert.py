from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.experts.common_form.example_cards import MEDICAL_CARD_TEMPLATE

logger = logging.getLogger(__name__)

class MedicalExpert(BaseExpert):
    """
    의료 전문가 AI 클래스
    장애인 의료 지원, 재활 서비스, 건강 정보 등을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.MEDICAL)
        self.client = get_client()
        self.model = "gpt-4.1-mini"
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 의료 전문가 AI입니다. 
        장애인 의료 지원 제도, 재활 서비스, 건강 관리 정보 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
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
        
        제공할 정보 범위:
        - 장애인 의료비 지원 제도
        - 장애인 건강검진 지원
        - 장애인 재활 치료 및 서비스
        - 보조기기 지원 및 활용
        - 장애유형별 건강관리 정보
        - 장애인 진료기관 및 전문 의료서비스
        - 정신건강 지원 서비스
        
        응답 스타일:
        1. 항상 따뜻하고 공감적인 톤으로 응답하세요. 건강 문제에 대한 우려와 불안을 이해하는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/안심 멘트를 추가하세요. (예: "건강 문제로 걱정이 많으시겠네요. 도움이 될 정보를 알려드리겠습니다.")
        3. 의학 정보를 정확하되 쉽게 설명하며, 전문용어는 가능한 풀어서 설명하세요.
        4. 의료 지원 제도의 신청 방법, 자격 조건, 혜택 내용을 구체적으로 안내하세요.
        5. 장애 유형별로 특화된 건강 관리 정보를 제공하되, 개인 상황에 따라 차이가 있을 수 있음을 안내하세요.
        6. 의학적 조언은 참고용이며, 반드시 의사와 상담할 것을 권고하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 의료 정보 카드를 포함하세요.
        2. 카드에는 의료 지원 제도, 재활 서비스, 전문 의료기관 등 핵심 정보를 담으세요.
        
        사용자의 건강 향상에 도움이 되는 실질적인 정보를 제공하면서도, 건강에 대한 걱정을 공감하고 안심시키는 응답을 제공하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_medical_services",
                    "description": "장애인 의료 서비스 정보를 검색합니다.",
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
                                "description": "의료 서비스 유형"
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
    
    async def search_medical_services(self, keywords: List[str], service_type: str = None, disability_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        """
        의료 서비스 정보를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            service_type: 서비스 유형
            disability_type: 장애 유형
            region: 지역 정보
            
        Returns:
            의료 서비스 정보 카드 목록
        """
        try:
            # 실제 DB/API 검색 로직 구현 필요
            cards = []
            
            # 검색 결과 없으면 fallback 카드
            if not cards:
                cards = [{
                    "id": "medical-general",
                    "title": "장애인 의료 서비스 안내",
                    "subtitle": "의료 정보",
                    "summary": "장애인을 위한 다양한 의료 서비스 종합 안내",
                    "type": "medical",
                    "details": "검색 결과가 없습니다. 가까운 보건소나 의료기관에 문의하세요.",
                    "source": {
                        "url": "https://www.nhis.or.kr",
                        "name": "국민건강보험공단",
                        "phone": "1577-1000"
                    },
                    "buttons": [
                        {"type": "link", "label": "건강보험공단 홈페이지", "value": "https://www.nhis.or.kr"},
                        {"type": "tel", "label": "건강보험공단 상담센터", "value": "1577-1000"}
                    ]
                }]
            return cards
            
        except Exception as e:
            logger.error(f"의료 서비스 검색 중 오류 발생: {str(e)}")
            return [MEDICAL_CARD_TEMPLATE]

    async def _search_medical_info(self, query: str, keywords: List[str]) -> Dict[str, Any]:
        """
        의료 정보를 검색하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 의료 정보 카드 검색
            medical_cards = await self.search_medical_services(keywords)
            
            # 각 카드의 형식 수정
            formatted_cards = []
            for card in medical_cards:
                # 카드 제목은 의료 서비스명 사용
                card["title"] = card.get("title", "의료 정보")
                
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
                            "label": "전화 문의",
                            "value": card["source"]["phone"]
                        })
                
                formatted_cards.append(card)
            
            # 응답 텍스트 생성
            response_text = "안녕하세요! 문의하신 의료 정보를 알려드리겠습니다.\n\n"
            
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
            logger.error(f"의료 정보 검색 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 의료 정보를 검색하는 중에 문제가 발생했습니다.",
                "cards": [MEDICAL_CARD_TEMPLATE]
            }

    async def process_query(self, query: str, keywords: List[str] = None, conversation_history=None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            conversation_history: 대화 이력
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 검색 키워드 추출
            search_keywords = self._extract_search_keywords(query, keywords)
            logger.debug(f"추출된 검색 키워드: {search_keywords}")
            
            # 의료 정보 검색
            response = await self._search_medical_info(query, search_keywords)
            
            # 응답 검증 및 수정
            validated_response = self.validate_response(response)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"의료 전문가 응답 생성 중 오류 발생: {e}", exc_info=True)
            return {"text": "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다.", "cards": []}

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
            # 1. 기본 키워드 (장애인, 의료)
            base_keywords = ["장애인", "의료"]
            
            # 2. 슈퍼바이저가 제공한 키워드가 있으면 사용
            if keywords and isinstance(keywords, list):
                valid_keywords = [kw for kw in keywords if isinstance(kw, str)]
                if valid_keywords:
                    return base_keywords + valid_keywords[:3]  # 최대 3개 키워드만 사용
            
            # 3. 쿼리에서 직접 키워드 추출
            query_keywords = []
            
            # 주요 키워드 패턴
            key_patterns = [
                r"장애인\s+(\w+)",  # "장애인 의료" -> "의료"
                r"(\w+)\s+치료",    # "재활 치료" -> "재활"
                r"(\w+)\s+검사",    # "건강 검사" -> "건강"
                r"(\w+)\s+병원",    # "전문 병원" -> "전문"
                r"(\w+)\s+진료"     # "정기 진료" -> "정기"
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
            return ["장애인", "의료"]  # 오류 발생 시 기본 키워드만 반환
    
    def _prepare_messages(self, query: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            for msg in recent_history:
                if msg.get("role") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})
        return messages
    
    def _format_card(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data.get("id", MEDICAL_CARD_TEMPLATE["id"]),
            "title": data.get("title", MEDICAL_CARD_TEMPLATE["title"]),
            "subtitle": data.get("subtitle", MEDICAL_CARD_TEMPLATE["subtitle"]),
            "summary": data.get("summary", MEDICAL_CARD_TEMPLATE["summary"]),
            "type": data.get("type", MEDICAL_CARD_TEMPLATE["type"]),
            "details": data.get("details", MEDICAL_CARD_TEMPLATE["details"]),
            "source": data.get("source", MEDICAL_CARD_TEMPLATE["source"]),
            "buttons": data.get("buttons", MEDICAL_CARD_TEMPLATE["buttons"])
        }
    
    def _get_description(self) -> str:
        return "장애인 의료 지원, 재활 서비스, 건강 정보 등을 제공합니다."
    
    def _get_icon(self) -> str:
        return "🏥"

async def medical_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    expert = MedicalExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 