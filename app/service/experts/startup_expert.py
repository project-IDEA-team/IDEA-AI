from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
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
        API 호출 대신 기본 데이터를 반환합니다.
        
        Args:
            keywords: 검색 키워드 목록
            startup_type: 창업 유형
            support_type: 지원 유형
            region: 지역 정보
            
        Returns:
            검색된 창업 정보 카드 목록
        """
        # 자금 지원 관련 키워드가 있으면 창업 자금 지원 정보 제공
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
        
        # 교육/컨설팅 관련 키워드가 있으면 창업 교육 정보 제공
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
                    "   - 사업개발비 지원: 연 1억원 한도\n"
                    "   - 세제 혜택: 법인세, 소득세, 취득세 등 감면\n"
                    "   - 공공기관 우선구매 대상\n\n"
                    "3. 지원 절차\n"
                    "   - 사회적기업가 육성사업 참여 → 예비사회적기업 지정 → 인증 사회적기업 신청\n"
                    "   - 사회적기업진흥원의 교육 및 컨설팅 지원 활용\n\n"
                    "4. 협동조합 설립 지원\n"
                    "   - 장애인 5인 이상 모여 설립 가능\n"
                    "   - 출자금 규모 제한 없음\n"
                    "   - 시·도지사에게 신고"
                ),
                "source": {
                    "url": "https://www.socialenterprise.or.kr",
                    "name": "한국사회적기업진흥원",
                    "phone": "031-697-7700"
                },
                "buttons": [
                    {"type": "link", "label": "사회적기업 안내", "value": "https://www.socialenterprise.or.kr"},
                    {"type": "tel", "label": "진흥원 문의", "value": "031-697-7700"}
                ]
            }]
        
        # 기본 창업 정보 카드 제공
        return [{
            "id": "startup-general",
            "title": "장애인 창업 종합 정보",
            "subtitle": "창업 안내",
            "summary": "장애인 창업에 필요한 기본 정보와 지원 제도 안내",
            "type": "startup",
            "details": (
                "장애인 창업을 위한 기본 정보와 지원 제도입니다.\n\n"
                "1. 장애인 창업 주요 지원기관\n"
                "   - 장애인기업종합지원센터: 창업 교육, 자금, 판로 등 지원\n"
                "   - 한국장애인개발원: 창업점포 지원사업 운영\n"
                "   - 소상공인시장진흥공단: 장애인 전용 정책자금 운영\n\n"
                "2. 주요 지원 제도\n"
                "   - 창업자금 지원: 최대 1억원 이상 저금리 융자\n"
                "   - 점포 지원: 임차보증금 지원\n"
                "   - 세제 혜택: 창업 후 일정기간 세금 감면\n"
                "   - 교육/컨설팅: 무료 창업 교육 및 전문가 컨설팅\n\n"
                "3. 창업 준비 절차\n"
                "   - 창업 교육 이수 → 사업계획 수립 → 자금 확보 → 입지 선정 → 사업자 등록 → 시설 구비 → 개업\n\n"
                "4. 장애유형별 추천 창업 분야\n"
                "   - 온라인 쇼핑몰, 디자인, 콘텐츠 제작, 마케팅, 컨설팅, 소셜벤처 등"
            ),
            "source": {
                "url": "https://www.debc.or.kr",
                "name": "장애인기업종합지원센터",
                "phone": "02-2181-6500"
            },
            "buttons": [
                {"type": "link", "label": "창업 지원 안내", "value": "https://www.debc.or.kr"},
                {"type": "tel", "label": "상담 문의", "value": "02-2181-6500"}
            ]
        }]
    
    async def process_query(self, query: str, keywords: List[str] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            conversation_history: 이전 대화 내용
            
        Returns:
            응답 정보
        """
        try:
            # 이전 대화 이력을 처리하고 메시지 배열 생성
            messages = self._prepare_messages(query, conversation_history)
            
            # 키워드가 없는 경우 빈 리스트로 초기화
            if not keywords:
                keywords = []
            
            # 창업 정보 카드 준비
            startup_cards = await self.search_startup_information(keywords)
            
            # LLM 응답 생성
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                response_format={"type": "text"},
                seed=42
            )
            
            # 응답 텍스트 추출
            response_text = response.choices[0].message.content.strip()
            
            # 최종 응답 생성
            return {
                "text": response_text,
                "cards": startup_cards
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