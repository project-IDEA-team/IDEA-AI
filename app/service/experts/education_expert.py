from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.experts.common_form.example_cards import EDUCATION_CARD_TEMPLATE

logger = logging.getLogger(__name__)

class EducationExpert(BaseExpert):
    """
    교육 전문가 AI 클래스
    장애인 교육 지원, 특수 교육, 교육 프로그램 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.EDUCATION)
        self.client = get_client()
        self.model = "gpt-4.1-mini"
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 교육 전문가 AI입니다. 
        장애인 교육 지원 제도, 특수교육, 학습 프로그램 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
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
        - 특수교육 제도 및 지원
        - 통합교육 및 일반학교 지원
        - 특수학교 및 특수학급 정보
        - 장애 유형별 교육 방법
        - 진학 및 진로 상담
        - 교육 보조기기 및 학습도구
        - 장학금 및 교육비 지원
        - 평생교육 및 성인교육
        
        응답 스타일:
        1. 항상 따뜻하고 격려하는 톤으로 응답하세요. 교육적 성장과 가능성을 강조하는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/격려 멘트를 추가하세요. (예: "교육에 관심을 가지고 계시는 모습이 정말 멋집니다. 함께 알아보겠습니다.")
        3. 교육 정보를 정확하고 이해하기 쉽게 설명하세요.
        4. 장애 특성에 맞는 맞춤형 교육 방법과 지원 제도를 안내하세요.
        5. 실질적인 교육 기회와 선택지를 제시하며, 다양한 가능성을 열어두세요.
        6. 학습자의 권리와 법적 지원 제도에 대해 안내하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 교육 정보 카드를 포함하세요.
        2. 카드에는 교육 프로그램, 학교 정보, 지원 제도 등 핵심 정보를 담으세요.
        
        사용자에게 실질적인 교육 정보와 기회를 제공하면서도, 교육적 성장과 가능성에 대한 희망을 함께 전달하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_education_information",
                    "description": "장애인 교육 정보를 검색합니다.",
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
                            "education_type": {
                                "type": "string",
                                "description": "교육 유형"
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
    
    async def search_education_information(self, keywords: List[str], education_type: str = None, disability_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        # 실제 DB/툴/외부API 호출로 대체 필요. 여기서는 fallback만 예시로 사용
        # 예시: DB에서 검색, 없으면 fallback
        # results = await self.db.search_education_by_keywords(keywords)
        results = []  # 실제 구현 시 DB/API 결과로 대체
        if results:
            return [self._format_card(r) for r in results]
        # fallback: 최소 안내 카드만 반환
        return [{**EDUCATION_CARD_TEMPLATE, "details": "검색 결과가 없습니다. 가까운 교육지원센터에 문의하세요."}]

    async def _search_education_info(self, query: str, keywords: List[str]) -> Dict[str, Any]:
        """
        교육 정보를 검색하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 교육 정보 카드 검색
            education_cards = await self.search_education_information(keywords)
            
            # 각 카드의 형식 수정
            formatted_cards = []
            for card in education_cards:
                # 카드 제목은 교육 프로그램명 사용
                card["title"] = card.get("title", "교육 정보")
                
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
            response_text = "안녕하세요! 문의하신 교육 정보를 알려드리겠습니다.\n\n"
            
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
            logger.error(f"교육 정보 검색 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 교육 정보를 검색하는 중에 문제가 발생했습니다.",
                "cards": [EDUCATION_CARD_TEMPLATE]
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
            
            # 교육 정보 검색
            response = await self._search_education_info(query, search_keywords)
            
            # 응답 검증 및 수정
            validated_response = self.validate_response(response)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"교육 전문가 응답 생성 중 오류 발생: {e}", exc_info=True)
            return {"text": "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다.", "cards": []}

    def _extract_search_keywords(self, query: str, keywords: List[str] = None) -> List[str]:
        """
        검색에 사용할 키워드를 추출합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            
        Returns:
            검색 키워드 목록
        """
        try:
            # 1. 기본 키워드 (장애인, 교육)
            base_keywords = ["장애인", "교육"]
            
            # 2. 슈퍼바이저가 제공한 키워드가 있으면 사용
            if keywords and isinstance(keywords, list):
                valid_keywords = [kw for kw in keywords if isinstance(kw, str)]
                if valid_keywords:
                    return base_keywords + valid_keywords[:3]  # 최대 3개 키워드만 사용
            
            # 3. 쿼리에서 직접 키워드 추출
            query_keywords = []
            
            # 주요 키워드 패턴
            key_patterns = [
                r"장애인\s+(\w+)",  # "장애인 교육" -> "교육"
                r"(\w+)\s+교육",    # "직업 교육" -> "직업"
                r"(\w+)\s+과정",    # "취업 과정" -> "취업"
                r"(\w+)\s+프로그램",  # "재활 프로그램" -> "재활"
                r"(\w+)\s+훈련"     # "직업 훈련" -> "직업"
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
            return ["장애인", "교육"]  # 오류 발생 시 기본 키워드만 반환
    
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
            "id": data.get("id", EDUCATION_CARD_TEMPLATE["id"]),
            "title": data.get("title", EDUCATION_CARD_TEMPLATE["title"]),
            "subtitle": data.get("subtitle", EDUCATION_CARD_TEMPLATE["subtitle"]),
            "summary": data.get("summary", EDUCATION_CARD_TEMPLATE["summary"]),
            "type": data.get("type", EDUCATION_CARD_TEMPLATE["type"]),
            "details": data.get("details", EDUCATION_CARD_TEMPLATE["details"]),
            "source": data.get("source", EDUCATION_CARD_TEMPLATE["source"]),
            "buttons": data.get("buttons", EDUCATION_CARD_TEMPLATE["buttons"])
        }
    
    def _get_description(self) -> str:
        return "장애인 교육 지원, 특수 교육, 교육 프로그램 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "🎓"

async def education_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    expert = EducationExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 