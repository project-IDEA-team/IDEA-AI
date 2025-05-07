from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.public_api.api_manager import ApiManager

logger = logging.getLogger(__name__)

class PolicyExpert(BaseExpert):
    """
    정책 전문가 AI 클래스
    장애인 관련 정책, 법률, 제도 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.POLICY)
        self.client = get_client()
        self.api_manager = ApiManager()
    
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
        
        Args:
            keywords: 검색 키워드 목록
            policy_type: 정책 유형
            
        Returns:
            검색된 정책 카드 목록
        """
        try:
            # ApiManager를 통해 공공데이터 API에서 정책 정보 검색
            policy_cards = await self.api_manager.search_by_keywords(keywords, "정책")
            
            # 검색 결과가 있으면 반환
            if policy_cards:
                return policy_cards
                
            # 검색 결과가 없는 경우 백업 데이터 활용
            # 2차 시도: 권리 보장 관련 키워드가 있으면 장애인차별금지법 정보 제공
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
            
            # 최후 방안: 기본 장애인 복지 정책 정보 제공
            return [{
                "id": "policy1",
                "title": "장애인연금제도",
                "subtitle": "기초생활보장제도",
                "summary": "장애인연금은 장애로 인한 추가적 비용을 지원하는 제도입니다.",
                "type": "policy",
                "details": "장애인연금은 장애로 인한 추가적 비용을 지원하는 제도로, 장애등급 1~2급 장애인에게 월 30만원을 지급합니다. 신청은 읍면동 주민센터에서 가능합니다.",
                "source": {
                    "url": "https://www.mohw.go.kr",
                    "name": "보건복지부",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.mohw.go.kr"},
                    {"type": "tel", "label": "전화 문의", "value": "129"}
                ]
            }]
            
        except Exception as e:
            logger.error(f"정책 검색 중 오류 발생: {e}")
            # 오류 발생 시 기본 데이터 반환
            return [{
                "id": "policy-error",
                "title": "장애인 복지 정책 안내",
                "subtitle": "종합 정보",
                "summary": "장애인을 위한 주요 복지 정책 종합 안내",
                "type": "policy",
                "details": (
                    "장애인을 위한 다양한 복지 정책이 있습니다:\n"
                    "- 장애인연금 및 장애수당\n"
                    "- 장애인 활동지원 서비스\n"
                    "- 장애인 의료비 지원\n"
                    "- 장애인 고용 지원\n"
                    "- 장애인 교육 지원\n\n"
                    "자세한 내용은 보건복지부 또는 주민센터에 문의하세요."
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
        사용자 쿼리를 처리하고 응답을 반환합니다.
        
        Args:
            query: 사용자 쿼리
            keywords: 슈퍼바이저가 추출한 키워드 목록
            conversation_history: 이전 대화 내용
            
        Returns:
            응답 및 정책 카드 정보
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
                        {"role": "system", "content": "사용자의 질문에서 장애인 정책 검색에 필요한 핵심 키워드를 5개 이내로 추출해주세요."},
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
            
            # 정책 데이터베이스 검색
            policy_cards = await self.search_policy_database(keywords)
            
            # 검색 결과 기반 응답 생성
            policy_titles = ", ".join([card["title"] for card in policy_cards[:3]])
            
            # 대화 이력을 LLM 메시지로 변환
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            
            # 이전 대화 내용이 있으면 메시지에 추가
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if content.strip():  # 내용이 있는 메시지만 추가
                        messages.append({"role": role, "content": content})
            
            # 마지막 질문과 정책 정보 포함
            messages.append({
                "role": "user", 
                "content": f"다음 질문에 대해 관련 정책 정보를 제공해주세요. 관련 정책: {policy_titles}\n\n질문: {query}"
            })
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "cards": policy_cards
            }
            
        except Exception as e:
            logger.error(f"정책 전문가 응답 생성 중 오류 발생: {e}")
            return {
                "answer": "죄송합니다. 현재 정책 정보를 제공하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "cards": []
            }
    
    def _get_description(self) -> str:
        return "정부, 지자체의 장애인 관련 법률 및 제도 안내"
    
    def _get_icon(self) -> str:
        return "📜"

async def policy_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    정책 전문가 응답을 생성합니다.
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 정책 카드 목록
    """
    expert = PolicyExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response["answer"], response["cards"] 