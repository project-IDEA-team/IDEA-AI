from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.public_api.api_manager import ApiManager

logger = logging.getLogger(__name__)

class WelfareExpert(BaseExpert):
    """
    복지 전문가 AI 클래스
    장애인 복지 제도, 서비스, 혜택 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.WELFARE)
        self.client = get_client()
        self.api_manager = ApiManager()
    
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
        try:
            # ApiManager를 통해 공공데이터 API에서 복지 정보 검색
            welfare_cards = await self.api_manager.search_by_keywords(keywords, "복지")
            
            # 검색 결과가 있으면 반환
            if welfare_cards:
                return welfare_cards
                
            # 검색 결과가 없는 경우 백업 데이터 활용
            # 2차 시도: 연금/수당 관련 키워드가 있으면 장애인연금 정보 제공
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
            
            # 3차 시도: 활동지원 관련 키워드가 있으면 활동지원 서비스 정보 제공
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
            
            # 감면혜택 관련 키워드가 있으면 감면혜택 정보 제공
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
                        "- TV 수신료 면제 등"
                    ),
                    "source": {
                        "url": "https://www.bokjiro.go.kr",
                        "name": "복지로",
                        "phone": "129"
                    },
                    "buttons": [
                        {"type": "link", "label": "감면혜택 안내", "value": "https://www.bokjiro.go.kr/discount"},
                        {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                    ]
                }]
            
            # 최후 방안: 기본 장애인 복지 서비스 정보 제공
            return [{
                "id": "welfare-1",
                "title": "장애인 복지 서비스 종합 안내",
                "subtitle": "복지서비스",
                "summary": "장애인을 위한 다양한 복지 서비스 안내",
                "type": "welfare",
                "details": (
                    "장애인을 위한 주요 복지 서비스 안내입니다.\n\n"
                    "경제적 지원:\n"
                    "- 장애인연금, 장애수당, 장애아동수당\n"
                    "- 의료비 지원, 보조기기 지원\n"
                    "- 각종 세제 혜택 및 요금 감면\n\n"
                    "일상생활 지원:\n"
                    "- 장애인 활동지원 서비스\n"
                    "- 장애아 가족 양육 지원\n"
                    "- 발달장애인 주간활동 서비스\n"
                    "- 보조기기 지원 및 대여\n\n"
                    "주거 지원:\n"
                    "- 주택 특별공급\n"
                    "- 주거환경 개선 사업\n\n"
                    "시설 이용:\n"
                    "- 장애인복지관, 주간보호시설\n"
                    "- 단기보호시설, 공동생활가정(그룹홈) 등"
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.bokjiro.go.kr"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
            
        except Exception as e:
            logger.error(f"복지 서비스 검색 중 오류 발생: {e}")
            # 오류 발생 시 기본 데이터 반환
            return [{
                "id": "welfare-error",
                "title": "장애인 복지 서비스 안내",
                "subtitle": "복지 안내",
                "summary": "장애인을 위한 주요 복지 서비스 안내",
                "type": "welfare",
                "details": (
                    "장애인을 위한 다양한 복지 서비스가 있습니다:\n"
                    "- 장애인연금 및 장애수당\n"
                    "- 장애인 활동지원 서비스\n"
                    "- 장애인 보조기기 지원\n"
                    "- 각종 감면 및 할인 혜택\n"
                    "- 주거 및 교육 지원 등\n\n"
                    "자세한 내용은 보건복지부 또는 주민센터에 문의하세요."
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "복지서비스 안내", "value": "https://www.bokjiro.go.kr"},
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
            응답 및 복지 서비스 카드 정보
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
                        {"role": "system", "content": "사용자의 질문에서 장애인 복지 서비스 검색에 필요한 핵심 키워드를 5개 이내로 추출해주세요."},
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
            
            # 복지 서비스 정보 검색
            welfare_cards = await self.search_welfare_services(keywords)
            
            # 검색 결과 기반 응답 생성
            service_titles = ", ".join([card["title"] for card in welfare_cards[:3]])
            
            # 대화 이력을 LLM 메시지로 변환
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            
            # 이전 대화 내용이 있으면 메시지에 추가
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if content.strip():  # 내용이 있는 메시지만 추가
                        messages.append({"role": role, "content": content})
            
            # 마지막 질문과 복지 서비스 정보 포함
            messages.append({
                "role": "user", 
                "content": f"다음 질문에 대해 관련 복지 서비스 정보를 제공해주세요. 관련 서비스: {service_titles}\n\n질문: {query}"
            })
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "cards": welfare_cards
            }
            
        except Exception as e:
            logger.error(f"복지 전문가 응답 생성 중 오류 발생: {e}")
            return {
                "answer": "죄송합니다. 현재 복지 서비스 정보를 제공하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "cards": []
            }
    
    def _get_description(self) -> str:
        return "복지 제도, 감면혜택, 활동지원 서비스 안내"
    
    def _get_icon(self) -> str:
        return "🏠"

async def welfare_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    복지 전문가 응답을 생성합니다.
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 복지 서비스 카드 목록
    """
    expert = WelfareExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response["answer"], response["cards"] 