from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
# from app.service.public_api.api_manager import ApiManager  # API 의존성 제거

logger = logging.getLogger(__name__)

class PolicyExpert(BaseExpert):
    """
    정책 전문가 AI 클래스
    장애인 관련 정책, 법률, 제도 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.POLICY)
        self.client = get_client()
        # self.api_manager = ApiManager()  # API 의존성 제거
        self.model = "gpt-4.1-mini"  # 사용할 모델 지정
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 정책 전문가 AI입니다. 
        장애인 관련 법률, 제도, 정책 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
        제공할 정보 범위:
        - 장애인복지법, 장애인차별금지법 등 관련 법률
        - 장애인연금, 장애수당 등 경제적 지원 제도
        - 장애인 활동지원 서비스
        - 장애인 편의시설 관련 규정
        - 장애인 이동권, 접근권 관련 정책
        - 장애인 고용 관련 정책 및 제도
        - 장애인 교육권 보장 정책
        
        응답 스타일:
        1. 항상 따뜻하고 공감적인 톤으로 응답하세요. 사용자의 상황과 어려움에 공감하는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/격려 멘트를 추가하세요. (예: "정책 정보를 찾고 계셨군요. 도움이 되는 정보를 알려드리겠습니다.")
        3. 최신 정보를 기반으로 정확한 내용을 제공하세요.
        4. 법률이나 제도의 근거를 명시하되, 전문용어는 가능한 쉽게 설명하세요.
        5. 신청 방법, 자격 요건, 지원 금액 등 실용적이고 구체적인 정보를 포함하세요.
        6. 관련 기관이나 문의처도 함께 안내하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 정책 정보 카드를 포함하세요.
        2. 카드에는 정책명, 간략한 설명, 신청 방법, 문의처 등 핵심 정보를 담으세요.
        
        사용자에게 실질적인 도움이 되는 정보를 제공하면서도, 정서적 지지를 함께 전달하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_policy_database",
                    "description": "장애인 정책 데이터베이스에서 관련 정보를 검색합니다.",
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
                            "policy_type": {
                                "type": "string",
                                "enum": ["경제지원", "의료지원", "교육지원", "고용지원", "주거지원", "이동지원", "문화지원", "기타"],
                                "description": "정책 유형"
                            }
                        },
                        "required": ["keywords"]
                    }
                }
            }
        ]
    
    async def search_policy_database(self, keywords: List[str], policy_type: str = None) -> List[Dict[str, Any]]:
        """
        키워드와 정책 유형을 기반으로 정책 데이터베이스를 검색합니다.
        API 호출 대신 기본 데이터를 반환합니다.
        
        Args:
            keywords: 검색 키워드 목록
            policy_type: 정책 유형
            
        Returns:
            검색된 정책 카드 목록
        """
        # 권리 보장 관련 키워드가 있으면 장애인차별금지법 정보 제공
        if any(kw in ["권리", "보장", "차별", "차별금지", "인권"] for kw in keywords):
            return [{
                "id": "right-1",
                "title": "장애인차별금지 및 권리구제 등에 관한 법률",
                "subtitle": "장애인 권리 보장",
                "summary": "장애인이 사회에서 차별받지 않고 평등한 권리를 누릴 수 있도록 보호하는 법",
                "type": "policy",
                "details": (
                    "법률명: 장애인차별금지 및 권리구제 등에 관한 법률\n"
                    "시행일: 2008년 4월 11일\n"
                    "주요내용:\n"
                    "- 장애인에 대한 차별 금지 및 권리 구제\n"
                    "- 장애인의 완전한 사회참여와 평등권 실현\n"
                    "- 교육, 고용, 서비스 등 다양한 영역에서의 차별 금지\n"
                    "신청방법: 차별 피해 시 국가인권위원회 또는 법원에 구제 신청 가능\n"
                    "구제절차: 국가인권위원회 진정 → 조사/조정/권고 → 시정명령 → 이행강제금\n"
                    "담당기관: 국가인권위원회, 보건복지부"
                ),
                "source": {
                    "url": "https://www.humanrights.go.kr",
                    "name": "국가인권위원회",
                    "phone": "1331"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.humanrights.go.kr"},
                    {"type": "tel", "label": "인권상담전화", "value": "1331"}
                ]
            }]
        
        # 기본 장애인 복지 정책 정보 제공
        return [{
            "id": "policy-general",
            "title": "장애인 복지 정책 종합 안내",
            "subtitle": "기본 정책 정보",
            "summary": "장애인을 위한 주요 복지 정책 안내",
            "type": "policy",
            "details": (
                "장애인을 위한 주요 정책 안내:\n\n"
                "1. 경제적 지원 정책\n"
                "- 장애인연금: 중증장애인 대상 기초급여와 부가급여 지원\n"
                "- 장애수당: 경증장애인 대상 소득 지원\n"
                "- 장애아동수당: 장애아동 양육 가정 지원\n\n"
                "2. 의료 지원 정책\n"
                "- 의료비 지원: 의료급여 2종 수급권자 등 대상\n"
                "- 건강보험료 경감: 저소득 장애인 가구 대상\n\n"
                "3. 교육 지원 정책\n"
                "- 특수교육 지원: 의무교육 실시 및 통합교육 지원\n"
                "- 장애대학생 도우미 지원: 대학 생활 지원\n\n"
                "4. 일자리 지원 정책\n"
                "- 장애인 의무고용제도: 국가 및 민간기업 장애인 고용 의무화\n"
                "- 장애인 고용장려금: 장애인 고용 사업주 지원\n\n"
                "자세한 내용은 보건복지부 또는 가까운 주민센터에 문의하세요."
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
            
            # 정책 정보 카드 준비
            policy_cards = await self.search_policy_database(keywords)
            
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
                "cards": policy_cards
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
        return "장애인 관련 법률, 제도, 정책 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "📜"

async def policy_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    정책 전문가 AI 응답 생성 함수
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 대화 이력
        
    Returns:
        (응답 텍스트, 정보 카드 목록)
    """
    expert = PolicyExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 