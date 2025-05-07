from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.public_api.api_manager import ApiManager

logger = logging.getLogger(__name__)

class StartupExpert(BaseExpert):
    """
    창업 전문가 AI 클래스
    장애인 창업 지원, 사업 운영, 창업 교육 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.STARTUP)
        self.client = get_client()
        self.api_manager = ApiManager()
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 창업 전문가 AI입니다. 
        장애인 창업 지원, 사업 운영, 창업 교육 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
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
                    "name": "search_startup_information",
                    "description": "장애인 창업 정보를 검색합니다.",
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
                            "startup_type": {
                                "type": "string",
                                "description": "창업 유형"
                            },
                            "support_type": {
                                "type": "string",
                                "description": "지원 유형"
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
    
    async def search_startup_information(self, keywords: List[str], startup_type: str = None, support_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        """
        키워드, 창업 유형, 지원 유형, 지역 등을 기반으로 창업 정보를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            startup_type: 창업 유형
            support_type: 지원 유형
            region: 지역 정보
            
        Returns:
            검색된 창업 정보 카드 목록
        """
        try:
            # ApiManager를 통해 공공데이터 API에서 창업 정보 검색
            startup_cards = await self.api_manager.search_by_keywords(keywords, "창업")
            
            # 검색 결과가 있으면 반환
            if startup_cards:
                return startup_cards
                
            # 검색 결과가 없는 경우 백업 데이터 활용
            # 2차 시도: 자금 지원 관련 키워드가 있으면 창업 자금 지원 정보 제공
            if any(kw in ["자금", "융자", "대출", "지원금", "투자"] for kw in keywords):
                return [{
                    "id": "startup-fund-1",
                    "title": "장애인 창업 자금 지원 제도",
                    "subtitle": "창업 자금",
                    "summary": "장애인 창업자를 위한 다양한 자금 지원 및 융자 제도",
                    "type": "startup",
                    "details": (
                        "장애인 창업자를 위한 다양한 자금 지원 제도입니다.\n\n"
                        "1. 장애인기업종합지원센터 창업 지원금\n"
                        "   - 지원규모: 최대 7천만원\n"
                        "   - 대상: 창업 예정이거나 3년 이내 장애인기업\n"
                        "   - 용도: 시설비, 장비구입비, 기술개발비 등\n"
                        "   - 신청: 한국장애인기업종합지원센터\n\n"
                        "2. 장애인 창업점포 지원사업\n"
                        "   - 지원규모: 최대 1억원 한도 임차보증금 지원\n"
                        "   - 조건: 5년 분할상환, 연 1~2% 이자\n"
                        "   - 신청: 한국장애인개발원\n\n"
                        "3. 장애인 전용 창업자금 융자\n"
                        "   - 지원규모: 최대 1억 2천만원\n"
                        "   - 조건: 최대 7년 대출, 우대금리 적용\n"
                        "   - 신청: 소상공인시장진흥공단\n\n"
                        "4. 사회적기업가 육성사업 창업 지원금\n"
                        "   - 지원규모: 팀당 5천만원 내외\n"
                        "   - 사회적 목적 실현 창업 아이템 보유자 대상\n"
                        "   - 신청: 한국사회적기업진흥원"
                    ),
                    "source": {
                        "url": "https://www.debc.or.kr",
                        "name": "장애인기업종합지원센터",
                        "phone": "02-2181-6500"
                    },
                    "buttons": [
                        {"type": "link", "label": "자금지원 안내", "value": "https://www.debc.or.kr/support/start-up"},
                        {"type": "tel", "label": "문의전화", "value": "02-2181-6500"}
                    ]
                }]
            
            # 3차 시도: 교육/컨설팅 관련 키워드가 있으면 창업 교육 정보 제공
            if any(kw in ["교육", "컨설팅", "멘토링", "상담", "코칭"] for kw in keywords):
                return [{
                    "id": "startup-education-1",
                    "title": "장애인 창업 교육 및 컨설팅",
                    "subtitle": "창업 교육",
                    "summary": "장애인 예비창업자 및 기창업자를 위한 교육 및 컨설팅 프로그램",
                    "type": "startup",
                    "details": (
                        "장애인 창업자를 위한 교육 및 컨설팅 프로그램입니다.\n\n"
                        "1. 장애인 맞춤형 창업교육\n"
                        "   - 내용: 창업 기초, 상권분석, 마케팅, 세무/회계, 온라인 창업 등\n"
                        "   - 대상: 예비창업자 및 업종전환 희망자\n"
                        "   - 비용: 무료\n"
                        "   - 신청: 장애인기업종합지원센터\n\n"
                        "2. 창업 멘토링 프로그램\n"
                        "   - 내용: 분야별 전문가와 1:1 멘토링\n"
                        "   - 대상: 창업 1년 이내 장애인기업\n"
                        "   - 분야: 마케팅, 재무, 상품개발, 온라인 판로 등\n"
                        "   - 신청: 장애인기업종합지원센터\n\n"
                        "3. 장애인 창업 컨설팅\n"
                        "   - 내용: 사업계획 수립, 입지선정, 행정절차 등 맞춤 컨설팅\n"
                        "   - 비용: 무료~일부 자부담\n"
                        "   - 신청: 소상공인시장진흥공단\n\n"
                        "4. 온라인 창업 강좌\n"
                        "   - 내용: 창업 전 과정 온라인 강의\n"
                        "   - 대상: 제한 없음\n"
                        "   - 접근: K-스타트업 홈페이지"
                    ),
                    "source": {
                        "url": "https://www.debc.or.kr",
                        "name": "장애인기업종합지원센터",
                        "phone": "02-2181-6500"
                    },
                    "buttons": [
                        {"type": "link", "label": "교육 프로그램", "value": "https://www.debc.or.kr/education"},
                        {"type": "tel", "label": "문의전화", "value": "02-2181-6500"}
                    ]
                }]
            
            # 사회적기업 관련 키워드가 있으면 사회적기업 창업 정보 제공
            if any(kw in ["사회적기업", "협동조합", "사회적경제", "소셜", "소셜벤처"] for kw in keywords):
                return [{
                    "id": "social-enterprise-1",
                    "title": "장애인 사회적기업 창업 지원",
                    "subtitle": "사회적기업",
                    "summary": "사회적 가치와 경제적 가치를 동시에 추구하는 사회적기업 창업 정보",
                    "type": "startup",
                    "details": (
                        "장애인이 설립하는 사회적기업에 대한 지원 정보입니다.\n\n"
                        "1. 사회적기업이란?\n"
                        "   - 취약계층에게 일자리나 사회서비스를 제공하며 사회적 목적을 추구하는 기업\n"
                        "   - 영업활동을 통한 수익 창출과 사회적 가치 실현을 동시에 추구\n\n"
                        "2. 장애인 사회적기업 인증 혜택\n"
                        "   - 인건비 지원: 최대 5년간 인건비 일부 지원\n"
                        "   - 경영지원: 전문 컨설팅, 홍보, 판로 지원\n"
                        "   - 세제 혜택: 법인세, 소득세, 취득세 등 감면\n"
                        "   - 공공조달 우대: 공공기관 우선구매 대상\n\n"
                        "3. 사회적기업가 육성사업\n"
                        "   - 내용: 창업비용, 멘토링, 사업화 지원 등\n"
                        "   - 대상: 사회문제 해결 아이디어를 가진 (예비)창업자\n"
                        "   - 지원금: 팀당 5천만원 내외\n"
                        "   - 신청: 한국사회적기업진흥원\n\n"
                        "4. 사회적기업 인증 절차\n"
                        "   - 예비사회적기업 지정 → 사회적기업 인증 신청 → 심사 및 인증"
                    ),
                    "source": {
                        "url": "https://www.socialenterprise.or.kr",
                        "name": "한국사회적기업진흥원",
                        "phone": "031-697-7700"
                    },
                    "buttons": [
                        {"type": "link", "label": "사회적기업 안내", "value": "https://www.socialenterprise.or.kr"},
                        {"type": "tel", "label": "문의전화", "value": "031-697-7700"}
                    ]
                }]
            
            # 최후 방안: 기본 장애인 창업 정보 제공
            return [{
                "id": "startup-info-1",
                "title": "장애인 창업 지원 종합 안내",
                "subtitle": "창업 지원",
                "summary": "장애인을 위한 다양한 창업 지원 제도 및 서비스 안내",
                "type": "startup",
                "details": (
                    "장애인 창업자를 위한 주요 지원 제도 및 서비스 안내입니다.\n\n"
                    "자금 지원:\n"
                    "- 장애인 전용 정책자금 융자\n"
                    "- 창업자금 지원 및 보조금\n"
                    "- 점포 임차보증금 지원\n\n"
                    "교육 및 컨설팅:\n"
                    "- 창업 기초 교육 프로그램\n"
                    "- 전문 멘토링 및 컨설팅\n"
                    "- 업종별 전문 교육\n\n"
                    "판로 지원:\n"
                    "- 장애인기업 제품 공공구매 지원\n"
                    "- 온라인 판로 지원\n"
                    "- 전시회 및 박람회 참가 지원\n\n"
                    "인증 및 혜택:\n"
                    "- 장애인기업 확인제도\n"
                    "- 사회적기업 인증\n"
                    "- 세제 혜택 및 정책 우대"
                ),
                "source": {
                    "url": "https://www.debc.or.kr",
                    "name": "장애인기업종합지원센터",
                    "phone": "02-2181-6500"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.debc.or.kr"},
                    {"type": "tel", "label": "창업상담", "value": "02-2181-6500"}
                ]
            }]
            
        except Exception as e:
            logger.error(f"창업 정보 검색 중 오류 발생: {e}")
            # 오류 발생 시 기본 데이터 반환
            return [{
                "id": "startup-error",
                "title": "장애인 창업 정보 안내",
                "subtitle": "창업 정보",
                "summary": "장애인을 위한 주요 창업 지원 제도 안내",
                "type": "startup",
                "details": (
                    "장애인을 위한 다양한 창업 지원 제도가 있습니다:\n"
                    "- 창업 자금 지원 및 융자\n"
                    "- 창업 교육 및 멘토링\n"
                    "- 장애인기업 판로 지원\n"
                    "- 사회적기업 지원\n"
                    "- 창업 컨설팅\n\n"
                    "자세한 내용은 장애인기업종합지원센터에 문의하세요."
                ),
                "source": {
                    "url": "https://www.debc.or.kr",
                    "name": "장애인기업종합지원센터",
                    "phone": "02-2181-6500"
                },
                "buttons": [
                    {"type": "link", "label": "창업지원 안내", "value": "https://www.debc.or.kr"},
                    {"type": "tel", "label": "창업상담", "value": "02-2181-6500"}
                ]
            }]
    
    async def process_query(self, query: str, keywords: List[str] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 응답을 반환합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            conversation_history: 이전 대화 내용
            
        Returns:
            응답 및 창업 정보 카드 정보
        """
        try:
            # 대화 기록이 없는 경우 기본값 설정
            if conversation_history is None:
                conversation_history = []
                
            # 키워드가 없는 경우 쿼리에서 추출
            if not keywords:
                extraction_response = await self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": "사용자의 질문에서 장애인 창업 정보 검색에 필요한 핵심 키워드를 5개 이내로 추출해주세요."},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.3
                )
                
                import json
                # 응답이 JSON 형식이 아닐 수 있으므로 처리
                try:
                    keywords_data = json.loads(extraction_response.choices[0].message.content)
                    keywords = keywords_data.get("keywords", [])
                except json.JSONDecodeError:
                    # 일반 텍스트에서 키워드 추출 시도
                    content = extraction_response.choices[0].message.content
                    possible_keywords = [k.strip() for k in content.split(',')]
                    keywords = [k for k in possible_keywords if k]
            
            # 창업 정보 검색
            startup_cards = await self.search_startup_information(keywords)
            
            # 검색 결과 기반 응답 생성
            service_titles = ", ".join([card["title"] for card in startup_cards[:3]])
            
            # 대화 이력을 LLM 메시지로 변환
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            
            # 이전 대화 내용이 있으면 메시지에 추가
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if content.strip():  # 내용이 있는 메시지만 추가
                        messages.append({"role": role, "content": content})
            
            # 마지막 질문과 창업 정보 포함
            messages.append({
                "role": "user", 
                "content": f"다음 질문에 대해 관련 창업 정보를 제공해주세요. 관련 서비스: {service_titles}\n\n질문: {query}"
            })
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "cards": startup_cards
            }
            
        except Exception as e:
            logger.error(f"창업 전문가 응답 생성 중 오류 발생: {e}")
            return {
                "answer": "죄송합니다. 현재 창업 정보를 제공하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "cards": []
            }
    
    def _get_description(self) -> str:
        return "창업 자금, 교육, 사회적기업 지원 정보 제공"
    
    def _get_icon(self) -> str:
        return "🚀"

async def startup_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    창업 전문가 응답을 생성합니다.
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 창업 정보 카드 목록
    """
    expert = StartupExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response["answer"], response["cards"] 