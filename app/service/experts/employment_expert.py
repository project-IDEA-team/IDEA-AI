from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client

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
        """
        키워드, 직업 유형, 지역 등을 기반으로 취업 정보 데이터베이스를 검색합니다.
        API 호출 대신 기본 데이터를 반환합니다.
        
        Args:
            keywords: 검색 키워드 목록
            job_type: 직업 유형 또는 산업 분야
            region: 지역 정보
            
        Returns:
            검색된 취업 정보 카드 목록
        """
        return [{
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
                "url": "https://www.kead.or.kr",
                "name": "한국장애인고용공단",
                "phone": "1588-1519"
            },
            "buttons": [
                {"type": "link", "label": "자세히 보기", "value": "https://www.kead.or.kr"},
                {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
            ]
        }]

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

    async def process_query(self, query: str, keywords: List[str] = None, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        사용자 쿼리를 처리하고 적절한 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 검색 키워드 목록
            conversation_history: 대화 이력
            
        Returns:
            응답 정보
        """
        try:
            # 이전 대화 이력을 처리하고 메시지 배열 생성
            messages = self._prepare_messages(query, conversation_history)
            
            # 추출된 키워드가 없는 경우 빈 리스트로 초기화
            if not keywords:
                keywords = []
            
            # 기본 취업 정보 카드
            job_cards = [{
                "id": "employment-info-1",
                "title": "장애인 취업 정보",
                "subtitle": "취업 지원",
                "summary": "장애인 취업을 위한 주요 정보와 지원 제도",
                "type": "employment",
                "details": (
                    "장애인 취업을 위한 주요 정보:\n\n"
                    "1. 한국장애인고용공단(KEAD)의 취업 지원 서비스\n"
                    "- 취업알선, 구직 상담, 직업능력평가 등 서비스 제공\n"
                    "- 전화 문의: 1588-1519\n\n"
                    "2. 장애인 고용장려금 제도\n"
                    "- 장애인 근로자를 고용한 사업주에게 지원금 지급\n\n"
                    "3. 근로지원인 서비스\n"
                    "- 업무 수행에 어려움이 있는 중증장애인에게 근로지원인 서비스 제공\n\n"
                    "4. 장애인 취업성공패키지\n"
                    "- 취업에 어려움을 겪는 장애인에게 단계별 취업 지원 서비스 제공"
                ),
                "source": {
                    "url": "https://www.kead.or.kr",
                    "name": "한국장애인고용공단",
                    "phone": "1588-1519"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.kead.or.kr"},
                    {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
                ]
            }]
            
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
                "cards": job_cards
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
        return "장애인 취업, 고용 지원, 직업 교육 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "💼"

async def employment_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    취업 전문가 AI 응답 생성 함수
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 대화 이력
        
    Returns:
        (응답 텍스트, 정보 카드 목록)
    """
    expert = EmploymentExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 