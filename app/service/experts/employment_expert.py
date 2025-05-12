from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.experts.common_form.example_cards import EMPLOYMENT_CARD_TEMPLATE

logger = logging.getLogger(__name__)

class EmploymentExpert(BaseExpert):
    """
    취업 전문가 AI 클래스
    장애인 취업, 고용 지원, 직업 교육 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.EMPLOYMENT)
        self.client = get_client()
        self.model = "gpt-4.1-mini"
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 취업 전문가 AI입니다. 
        장애인 취업, 고용 지원, 직업 교육 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
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
        - 장애인 의무고용제도
        - 장애인 구인구직 정보
        - 장애인 표준사업장 정보
        - 장애인 직업훈련 프로그램
        - 취업 후 근로지원 서비스
        - 장애인 취업 관련 보조금 및 지원금
        - 장애인 창업 지원 정보
        
        응답 스타일:
        1. 항상 따뜻하고 격려하는 톤으로 응답하세요. 구직자의 어려움에 공감하고 희망을 주는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/격려 멘트를 추가하세요. (예: "취업 준비가 쉽지 않으시죠. 함께 좋은 정보를 찾아보겠습니다.")
        3. 최신 고용 동향과 정보를 기반으로 실용적인 조언을 제공하세요.
        4. 취업 지원 제도와 프로그램에 대해 구체적으로 설명하되, 지원 자격, 신청 방법, 혜택 등을 명확히 안내하세요.
        5. 가능한 많은 취업 기회를 제공하고, 다양한 직업 영역을 탐색하도록 격려하세요.
        6. 취업 후 적응과 지속적인 근무를 위한 정보도 함께 제공하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 취업 정보 카드를 포함하세요.
        2. 카드에는 구인 정보, 직업훈련 프로그램, 취업지원 서비스 등 핵심 정보를 담으세요.
        
        사용자에게 실질적인 취업 기회와 정보를 제공하면서도, 심리적 지지와 자신감을 키워주는 응답을 제공하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_employment_database",
                    "description": "장애인 취업 데이터베이스에서 관련 정보를 검색합니다.",
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
                            "job_type": {
                                "type": "string",
                                "description": "직업 유형 또는 산업 분야"
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
    
    async def search_employment_database(self, keywords: List[str], job_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        # 실제 DB/툴/외부API 호출로 대체 필요. 여기서는 fallback만 예시로 사용
        results = []  # 실제 구현 시 DB/API 결과로 대체
        if results:
            return [self._format_card(r) for r in results]
        return [{**EMPLOYMENT_CARD_TEMPLATE, "details": "검색 결과가 없습니다. 가까운 고용센터에 문의하세요."}]

    async def get_job_list_by_condition(self, disk_no=None, bsns_spcm_cd=None, bsns_cond_cd=None, page=1, size=10) -> List[Dict[str, Any]]:
        """장애인 구인 정보를 조건으로 검색합니다. API 호출 대신 기본 데이터를 반환합니다."""
        return [{
            "id": "job-listing-1",
            "title": "사무보조 (장애인 우대)",
            "company": "OO기업",
            "location": "서울 강남구",
            "salary": "월 200만원",
            "requirements": "경력무관, 고졸이상",
            "description": "장애인 의무고용 기업에서 사무보조 인력을 모집합니다.",
            "deadline": "채용시까지",
            "contact": "02-123-4567"
        }]

    async def get_job_list_by_date(self, disk_no=None, reg_date=None, clos_date=None, page=1, size=10) -> List[Dict[str, Any]]:
        """장애인 구인 정보를 날짜로 검색합니다. API 호출 대신 기본 데이터를 반환합니다."""
        return [{
            "id": "job-listing-2",
            "title": "웹 디자이너 (장애인 전형)",
            "company": "XX디자인",
            "location": "서울 마포구",
            "salary": "월 250만원",
            "requirements": "경력 1년 이상, 디자인 전공자 우대",
            "description": "장애인 친화적 환경에서 웹 디자인 업무를 담당할 인재를 찾습니다.",
            "deadline": "2023년 12월 31일",
            "contact": "02-987-6543"
        }]

    async def get_job_detail(self, wanted_auth_no) -> Dict[str, Any]:
        """장애인 구인 상세 정보를 조회합니다. API 호출 대신 기본 데이터를 반환합니다."""
        return {
            "id": wanted_auth_no,
            "title": "데이터 입력 사무원",
            "company": "주식회사 데이터월드",
            "location": "서울 금천구",
            "salary": "월 185만원",
            "working_hours": "09:00-18:00 (주 5일)",
            "benefits": "4대보험, 중식제공, 통근버스",
            "requirements": "장애인, 고졸이상, 컴퓨터 활용능력 필수",
            "job_description": "엑셀을 활용한 데이터 입력 및 관리 업무",
            "application_method": "이메일 지원 (resume@example.com)",
            "contact_info": "담당자: 김채용 / 02-345-6789",
            "deadline": "2023년 12월 15일"
        }

    async def _search_employment_info(self, query: str, keywords: List[str]) -> Dict[str, Any]:
        """
        취업 정보를 검색하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            
        Returns:
            응답 딕셔너리 (text, cards)
        """
        try:
            # 취업 정보 카드 검색
            employment_cards = await self.search_employment_database(keywords)
            
            # 각 카드의 형식 수정
            formatted_cards = []
            for card in employment_cards:
                # 카드 제목은 채용/지원 프로그램명 사용
                card["title"] = card.get("title", "취업 정보")
                
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
            response_text = "안녕하세요! 문의하신 취업 정보를 알려드리겠습니다.\n\n"
            
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
            logger.error(f"취업 정보 검색 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 취업 정보를 검색하는 중에 문제가 발생했습니다.",
                "cards": [EMPLOYMENT_CARD_TEMPLATE]
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
            
            # 취업 정보 검색
            response = await self._search_employment_info(query, search_keywords)
            
            # 응답 검증 및 수정
            validated_response = self.validate_response(response)
            
            return validated_response
            
        except Exception as e:
            logger.error(f"취업 전문가 응답 생성 중 오류 발생: {e}", exc_info=True)
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
            # 1. 기본 키워드 (장애인, 취업)
            base_keywords = ["장애인", "취업"]
            
            # 2. 슈퍼바이저가 제공한 키워드가 있으면 사용
            if keywords and isinstance(keywords, list):
                valid_keywords = [kw for kw in keywords if isinstance(kw, str)]
                if valid_keywords:
                    return base_keywords + valid_keywords[:3]  # 최대 3개 키워드만 사용
            
            # 3. 쿼리에서 직접 키워드 추출
            query_keywords = []
            
            # 주요 키워드 패턴
            key_patterns = [
                r"장애인\s+(\w+)",  # "장애인 취업" -> "취업"
                r"(\w+)\s+채용",    # "공공기관 채용" -> "공공기관"
                r"(\w+)\s+일자리",  # "사무직 일자리" -> "사무직"
                r"(\w+)\s+구직",    # "정규직 구직" -> "정규직"
                r"(\w+)\s+기업"     # "대기업 기업" -> "대기업"
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
            return ["장애인", "취업"]  # 오류 발생 시 기본 키워드만 반환
    
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
            "id": data.get("id", EMPLOYMENT_CARD_TEMPLATE["id"]),
            "title": data.get("title", EMPLOYMENT_CARD_TEMPLATE["title"]),
            "subtitle": data.get("subtitle", EMPLOYMENT_CARD_TEMPLATE["subtitle"]),
            "summary": data.get("summary", EMPLOYMENT_CARD_TEMPLATE["summary"]),
            "type": data.get("type", EMPLOYMENT_CARD_TEMPLATE["type"]),
            "details": data.get("details", EMPLOYMENT_CARD_TEMPLATE["details"]),
            "source": data.get("source", EMPLOYMENT_CARD_TEMPLATE["source"]),
            "buttons": data.get("buttons", EMPLOYMENT_CARD_TEMPLATE["buttons"])
        }
    
    def _get_description(self) -> str:
        return "장애인 취업, 고용 지원, 직업 교육 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "💼"

async def employment_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    expert = EmploymentExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 