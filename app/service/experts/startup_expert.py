from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.experts.common_form.example_cards import STARTUP_CARD_TEMPLATE
# from app.service.public_api.api_manager import ApiManager  # API 의존성 제거

logger = logging.getLogger(__name__)

class StartupExpert(BaseExpert):
    """
    창업 전문가 AI 클래스
    장애인 창업 지원, 사업 운영, 창업 교육 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.STARTUP)
        self.client = get_client()
        # self.api_manager = ApiManager()  # API 의존성 제거
        self.model = "gpt-4.1-mini"  # 사용할 모델 지정
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 창업 전문가 AI입니다. 
        장애인 창업 지원, 사업 운영, 창업 교육 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
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
        - 장애인 창업 지원 정책 및 제도
        - 장애인 창업 자금 지원 및 융자
        - 장애인 적합 창업 아이템
        - 창업 교육 및 컨설팅 프로그램
        - 장애인기업 인증 및 혜택
        - 사회적기업, 협동조합 등 사회적 경제 창업
        - 업종별 창업 절차 및 필요 서류
        - 성공 사례 및 실패 사례 분석
        
        응답 스타일:
        1. 항상 따뜻하고 격려하는 톤으로 응답하세요. 창업의 가능성을 강조하는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/격려 멘트를 추가하세요. (예: "창업에 관심을 가지고 계시는군요. 함께 좋은 정보를 찾아보겠습니다.")
        3. 창업 정보를 정확하고 실용적으로 제공하되, 현실적인 어려움과 극복 방법도 함께 안내하세요.
        4. 장애 특성을 고려한 맞춤형 창업 아이템이나 운영 방식을 제안하세요.
        5. 자금 지원, 세제 혜택 등 실질적인 지원 정보를 상세히 안내하세요.
        6. 신청 방법, 필요 서류, 담당 기관 등 구체적인 정보를 포함하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 창업 정보 카드를 포함하세요.
        2. 카드에는 지원 프로그램, 자금 지원 제도, 창업 교육 등 핵심 정보를 담으세요.
        
        사용자에게 실질적인 창업 정보와 기회를 제공하면서도, 성공적인 창업에 대한 자신감과 희망을 함께 전달하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_startup_services",
                    "description": "장애인 창업 서비스 정보를 검색합니다.",
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
                                "description": "창업 서비스 유형"
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
    
    async def search_startup_services(self, keywords: List[str], service_type: str = None, disability_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        """
        창업 서비스 정보를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            service_type: 서비스 유형
            disability_type: 장애 유형
            region: 지역 정보
            
        Returns:
            창업 서비스 정보 카드 목록
        """
        try:
            # 실제 DB/API 검색 로직 구현 필요
            cards = []
            
            # 검색 결과 없으면 fallback 카드
            if not cards:
                cards = [{
                    "id": "startup-general",
                    "title": "장애인 창업 지원 안내",
                    "subtitle": "창업 정보",
                    "summary": "장애인을 위한 다양한 창업 지원 서비스 종합 안내",
                    "type": "startup",
                    "details": "검색 결과가 없습니다. 가까운 장애인기업종합지원센터에 문의하세요.",
                    "source": {
                        "url": "https://www.debc.or.kr",
                        "name": "장애인기업종합지원센터",
                        "phone": "1588-6072"
                    },
                    "buttons": [
                        {"type": "link", "label": "장애인기업종합지원센터 홈페이지", "value": "https://www.debc.or.kr"},
                        {"type": "tel", "label": "창업 상담 문의", "value": "1588-6072"}
                    ]
                }]
            return cards
            
        except Exception as e:
            logger.error(f"창업 서비스 검색 중 오류 발생: {str(e)}")
            return [STARTUP_CARD_TEMPLATE]

    async def _search_startup_info(self, query: str, keywords: List[str]) -> Dict[str, Any]:
        """
        창업 정보를 검색하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 창업 정보 카드 검색
            startup_cards = await self.search_startup_services(keywords)
            
            # 각 카드의 형식 수정
            formatted_cards = []
            for card in startup_cards:
                # 카드 제목은 창업 지원 프로그램명 사용
                card["title"] = card.get("title", "창업 정보")
                
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
            response_text = "안녕하세요! 문의하신 창업 정보를 알려드리겠습니다.\n\n"
            
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
            logger.error(f"창업 정보 검색 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 창업 정보를 검색하는 중에 문제가 발생했습니다.",
                "cards": [STARTUP_CARD_TEMPLATE]
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
            
            # 창업 정보 검색
            response = await self._search_startup_info(query, search_keywords)
            
            # 응답 검증 및 수정
            validated_response = self.validate_response(response)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"창업 전문가 응답 생성 중 오류 발생: {e}", exc_info=True)
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
            # 1. 기본 키워드 (장애인, 창업)
            base_keywords = ["장애인", "창업"]
            
            # 2. 슈퍼바이저가 제공한 키워드가 있으면 사용
            if keywords and isinstance(keywords, list):
                valid_keywords = [kw for kw in keywords if isinstance(kw, str)]
                if valid_keywords:
                    return base_keywords + valid_keywords[:3]  # 최대 3개 키워드만 사용
            
            # 3. 쿼리에서 직접 키워드 추출
            query_keywords = []
            
            # 주요 키워드 패턴
            key_patterns = [
                r"장애인\s+(\w+)",  # "장애인 창업" -> "창업"
                r"(\w+)\s+창업",    # "카페 창업" -> "카페"
                r"(\w+)\s+사업",    # "온라인 사업" -> "온라인"
                r"(\w+)\s+자금",    # "지원 자금" -> "지원"
                r"(\w+)\s+교육"     # "창업 교육" -> "창업"
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
            return ["장애인", "창업"]  # 오류 발생 시 기본 키워드만 반환
    
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
            "id": data.get("id", STARTUP_CARD_TEMPLATE["id"]),
            "title": data.get("title", STARTUP_CARD_TEMPLATE["title"]),
            "subtitle": data.get("subtitle", STARTUP_CARD_TEMPLATE["subtitle"]),
            "summary": data.get("summary", STARTUP_CARD_TEMPLATE["summary"]),
            "type": data.get("type", STARTUP_CARD_TEMPLATE["type"]),
            "details": data.get("details", STARTUP_CARD_TEMPLATE["details"]),
            "source": data.get("source", STARTUP_CARD_TEMPLATE["source"]),
            "buttons": data.get("buttons", STARTUP_CARD_TEMPLATE["buttons"])
        }
    
    def _get_description(self) -> str:
        return "장애인 창업 지원, 사업 운영, 창업 교육 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "🏢"

async def startup_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    창업 전문가 AI 응답 생성 함수
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 대화 이력
        
    Returns:
        (응답 텍스트, 정보 카드 목록)
    """
    expert = StartupExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 