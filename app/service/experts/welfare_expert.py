from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client

logger = logging.getLogger(__name__)

class WelfareExpert(BaseExpert):
    """
    복지 전문가 AI 클래스
    장애인 복지 제도, 서비스, 혜택 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.WELFARE)
        self.client = get_client()
        self.model = "gpt-4.1-mini"
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 복지 전문가 AI입니다. 
        장애인 복지 제도, 서비스, 혜택 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
        제공할 정보 범위:
        - 장애인 등록 및 장애 판정
        - 장애인 연금 및 수당
        - 장애인 감면/할인 혜택
        - 장애인 활동지원 서비스
        - 장애인 보조기기 지원
        - 장애인 주거 지원
        - 장애인 가족 지원
        - 지역별 복지시설 및 이용 방법
        
        응답 스타일:
        1. 항상 따뜻하고 공감적인 톤으로 응답하세요. 사용자의 상황을 이해하고 위로하는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/격려 멘트를 추가하세요. (예: "어려운 상황에서도 정보를 찾는 노력에 응원을 보냅니다.")
        3. 복지 제도와 서비스에 대해 정확하고 구체적으로 설명하세요.
        4. 신청 방법, 필요 서류, 담당 기관 등 실질적인 정보를 포함하세요.
        5. 복지 서비스를 받을 수 있는 자격 요건을 명확히 안내하세요.
        6. 제도 이용 시 주의사항이나 팁도 함께 제공하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 복지 정보 카드를 포함하세요.
        2. 카드에는 서비스명, 지원 내용, 신청 방법, 문의처 등 핵심 정보를 담으세요.
        
        사용자에게 실질적인 도움이 되는 복지 정보를 제공하면서도, 정서적 지지와 용기를 함께 전달하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_welfare_services",
                    "description": "장애인 복지 서비스 정보를 검색합니다.",
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
                                "description": "복지 서비스 유형"
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
    
    async def search_welfare_services(self, keywords: List[str], service_type: str = None, disability_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        """
        키워드, 서비스 유형, 장애 유형, 지역 등을 기반으로 복지 서비스 정보를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            service_type: 복지 서비스 유형
            disability_type: 장애 유형
            region: 지역 정보
            
        Returns:
            검색된 복지 서비스 카드 목록
        """
        if any(kw in ["연금", "수당", "급여", "지원금", "돈"] for kw in keywords):
            return [{
                "id": "pension-1",
                "title": "장애인연금",
                "subtitle": "소득지원",
                "summary": "중증장애인의 생활 안정을 위한 소득지원 제도",
                "type": "welfare",
                "details": (
                    "장애인연금은 중증장애인의 생활 안정을 위해 매월 일정 금액을 지급하는 제도입니다.\n\n"
                    "지원대상:\n"
                    "- 만 18세 이상의 등록 중증장애인\n"
                    "- 본인과 배우자의 소득인정액이 선정기준액 이하인 자\n\n"
                    "지원내용:\n"
                    "- 기초급여: 월 최대 300,000원\n"
                    "- 부가급여: 월 20,000원~380,000원(대상자별 차등)\n\n"
                    "신청방법:\n"
                    "- 주소지 관할 읍·면·동 주민센터 방문 신청\n"
                    "- 복지로 홈페이지 온라인 신청\n\n"
                    "구비서류:\n"
                    "- 사회보장급여 신청서\n"
                    "- 소득·재산 확인 서류\n"
                    "- 통장 사본, 장애인 증명서 등"
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "제도 안내", "value": "https://www.bokjiro.go.kr/pension"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
        
        if any(kw in ["활동", "활동지원", "돌봄", "도움", "도우미"] for kw in keywords):
            return [{
                "id": "activity-1",
                "title": "장애인 활동지원 서비스",
                "subtitle": "일상생활 지원",
                "summary": "장애인의 자립생활과 사회참여를 지원하는 서비스",
                "type": "welfare",
                "details": (
                    "장애인 활동지원 서비스는 혼자서 일상생활과 사회활동이 어려운 장애인에게 활동지원사를 파견하여 지원하는 서비스입니다.\n\n"
                    "지원대상:\n"
                    "- 만 6세 이상 ~ 65세 미만 등록 장애인\n"
                    "- 활동지원 신청조사표에 의한 방문조사 결과 220점 이상인 자\n\n"
                    "지원내용:\n"
                    "- 신체활동 지원: 목욕, 식사, 세면, 옷 갈아입기 등\n"
                    "- 가사활동 지원: 청소, 세탁, 식사 준비 등\n"
                    "- 사회활동 지원: 외출, 쇼핑, 여가활동, 직장생활 등\n"
                    "- 방문목욕, 방문간호 등\n\n"
                    "신청방법:\n"
                    "- 주소지 관할 읍·면·동 주민센터 방문 신청\n\n"
                    "본인부담금: 소득수준에 따라 차등 부과"
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "서비스 안내", "value": "https://www.bokjiro.go.kr/activity-support"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
        
        if any(kw in ["감면", "할인", "혜택", "요금", "공제"] for kw in keywords):
            return [{
                "id": "discount-1",
                "title": "장애인 감면혜택",
                "subtitle": "요금 감면 및 할인",
                "summary": "장애인을 위한 각종 요금 감면 및 할인 혜택",
                "type": "welfare",
                "details": (
                    "장애인을 위한 다양한 감면 및 할인 혜택이 있습니다.\n\n"
                    "교통 관련:\n"
                    "- 철도: 1~3급 장애인 본인 및 보호자 1인 50% 할인\n"
                    "- 항공: 국내선 50% 할인(중증), 30% 할인(경증)\n"
                    "- 고속버스: 50% 할인(중증), 30% 할인(경증)\n"
                    "- 자동차: 자동차세, 등록세, LPG 연료 사용 허용 등\n\n"
                    "문화생활:\n"
                    "- 국립공원, 고궁, 박물관 무료 입장\n"
                    "- 영화관, 공연장 할인\n\n"
                    "통신 요금:\n"
                    "- 이동통신 기본료 및 통화료 35% 할인\n"
                    "- 인터넷, 유선전화 등 감면\n\n"
                    "공과금:\n"
                    "- 전기요금: 월 최대 16,000원 할인\n"
                    "- 상하수도 요금 감면\n"
                    "- TV 수신료 면제(시청각 장애인)"
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.bokjiro.go.kr/discount"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
        
        return [{
            "id": "welfare-general",
            "title": "장애인 복지 서비스 안내",
            "subtitle": "복지 정보",
            "summary": "장애인을 위한 다양한 복지 서비스 종합 안내",
            "type": "welfare",
            "details": (
                "장애인을 위한 주요 복지 서비스 안내입니다:\n\n"
                "1. 장애인연금 및 장애수당\n"
                "2. 장애인 활동지원 서비스\n"
                "3. 장애인 보조기기 지원\n"
                "4. 장애인 주택 특별공급\n"
                "5. 장애인 감면 및 할인 혜택\n"
                "6. 장애인 의료 및 재활 지원\n"
                "7. 장애아동 가족 지원\n\n"
                "자세한 내용은 가까운 주민센터나 보건복지상담센터(129)로 문의하세요."
            ),
            "source": {
                "url": "https://www.bokjiro.go.kr",
                "name": "복지로",
                "phone": "129"
            },
            "buttons": [
                {"type": "link", "label": "복지로 홈페이지", "value": "https://www.bokjiro.go.kr"},
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
            messages = self._prepare_messages(query, conversation_history)
            
            if not keywords:
                keywords = []
            
            welfare_cards = await self.search_welfare_services(keywords)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                response_format={"type": "text"},
                seed=42
            )
            
            response_text = response.choices[0].message.content.strip()
            
            return {
                "text": response_text,
                "cards": welfare_cards
            }
            
        except Exception as e:
            logger.error(f"응답 생성 중 오류 발생: {str(e)}")
            return {
                "text": "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다. 다시 시도해 주세요.",
                "cards": []
            }
    
    def _prepare_messages(self, query: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            for msg in recent_history:
                if msg.get("role") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def _get_description(self) -> str:
        return "장애인 복지 서비스, 혜택 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "🏥"

async def welfare_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    복지 전문가 AI 응답 생성 함수
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 대화 이력
        
    Returns:
        (응답 텍스트, 정보 카드 목록)
    """
    expert = WelfareExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 