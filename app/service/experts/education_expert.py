from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client
from app.service.public_api.api_manager import ApiManager

logger = logging.getLogger(__name__)

class EducationExpert(BaseExpert):
    """
    교육 전문가 AI 클래스
    장애인 교육 지원, 특수 교육, 교육 프로그램 등에 대한 정보를 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.EDUCATION)
        self.client = get_client()
        self.api_manager = ApiManager()
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 교육 전문가 AI입니다. 
        장애인 교육 지원 제도, 특수교육, 학습 프로그램 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
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
        """
        키워드, 교육 유형, 장애 유형, 지역 등을 기반으로 교육 정보를 검색합니다.
        
        Args:
            keywords: 검색 키워드 목록
            education_type: 교육 유형
            disability_type: 장애 유형
            region: 지역 정보
            
        Returns:
            검색된 교육 정보 카드 목록
        """
        try:
            # ApiManager를 통해 공공데이터 API에서 교육 정보 검색
            education_cards = await self.api_manager.search_by_keywords(keywords, "교육")
            
            # 검색 결과가 있으면 반환
            if education_cards:
                return education_cards
                
            # 검색 결과가 없는 경우 백업 데이터 활용
            # 2차 시도: 특수교육 관련 키워드가 있으면 특수교육 정보 제공
            if any(kw in ["특수교육", "특수학교", "통합교육", "개별화", "IEP"] for kw in keywords):
                return [{
                    "id": "special-education-1",
                    "title": "특수교육 지원 제도",
                    "subtitle": "특수교육",
                    "summary": "장애학생을 위한 특수교육 제도 및 지원 서비스 안내",
                    "type": "education",
                    "details": (
                        "특수교육 지원 제도는 장애가 있는 학생에게 적합한 교육환경과 서비스를 제공하는 제도입니다.\n\n"
                        "주요 내용:\n"
                        "- 특수교육대상자 선정: 교육지원청 특수교육지원센터의 진단·평가 후 특수교육운영위원회 심의를 거쳐 선정\n"
                        "- 개별화교육계획(IEP): 학생의 능력과 특성에 맞는 맞춤형 교육 계획 수립 및 실행\n"
                        "- 교육환경: 특수학교, 특수학급, 일반학급 통합교육 등 다양한 배치 옵션\n"
                        "- 관련서비스: 상담지원, 가족지원, 치료지원, 보조인력 지원, 보조공학기기 지원 등\n"
                        "- 순회교육: 이동이 불편한 장애학생을 위한 교사 방문 교육\n\n"
                        "신청방법: 거주지 교육지원청 특수교육지원센터에 문의 및 신청"
                    ),
                    "source": {
                        "url": "https://www.nise.go.kr",
                        "name": "국립특수교육원",
                        "phone": "041-537-1500"
                    },
                    "buttons": [
                        {"type": "link", "label": "특수교육 안내", "value": "https://www.nise.go.kr"},
                        {"type": "tel", "label": "국립특수교육원", "value": "041-537-1500"}
                    ]
                }]
            
            # 3차 시도: 장학금/교육비 관련 키워드가 있으면 교육비 지원 정보 제공
            if any(kw in ["장학금", "교육비", "학비", "지원금", "바우처"] for kw in keywords):
                return [{
                    "id": "education-cost-1",
                    "title": "장애학생 교육비 지원",
                    "subtitle": "교육비 지원",
                    "summary": "장애학생의 교육비 부담 경감을 위한 다양한 지원 제도",
                    "type": "education",
                    "details": (
                        "장애학생을 위한 다양한 교육비 지원 제도입니다.\n\n"
                        "대표적인 지원 제도:\n"
                        "- 특수교육대상자 의무교육: 유치원~고등학교 과정 무상교육 제공\n"
                        "- 장애인 대학생 도우미 지원: 대학 생활 지원 인력 제공\n"
                        "- 장애대학생 교육활동 지원: 교재제작, 보조기기 대여 등\n"
                        "- 장애인 평생교육 바우처: 연간 35만원 이내 평생교육 비용 지원\n"
                        "- 발달재활서비스: 만 18세 미만 장애아동 대상 월 14~22만원 지원\n"
                        "- 장애인 정보화교육: 무료 정보화 교육 제공\n\n"
                        "신청방법: 각 지원별로 상이하므로 해당 기관에 문의\n"
                        "- 특수교육: 교육지원청 특수교육지원센터\n"
                        "- 대학지원: 각 대학 장애학생지원센터\n"
                        "- 평생교육바우처: 국가평생교육진흥원"
                    ),
                    "source": {
                        "url": "https://www.nise.go.kr",
                        "name": "국립특수교육원",
                        "phone": "041-537-1500"
                    },
                    "buttons": [
                        {"type": "link", "label": "지원제도 안내", "value": "https://www.nise.go.kr/main.do?s=nise"},
                        {"type": "tel", "label": "문의전화", "value": "041-537-1500"}
                    ]
                }]
            
            # 평생교육 관련 키워드가 있으면 평생교육 정보 제공
            if any(kw in ["평생교육", "성인교육", "평생", "평생학습", "사회교육"] for kw in keywords):
                return [{
                    "id": "lifelong-education-1",
                    "title": "장애인 평생교육 지원",
                    "subtitle": "평생교육",
                    "summary": "성인 장애인의 지속적인 교육과 역량 개발을 위한 평생교육 프로그램",
                    "type": "education",
                    "details": (
                        "장애인 평생교육은 학령기 이후 성인 장애인의 지속적인 교육과 사회참여를 지원하는 프로그램입니다.\n\n"
                        "주요 프로그램:\n"
                        "- 학력보완교육: 문해교육, 학력취득 과정\n"
                        "- 직업능력교육: 직업 기초 및 응용 기술 교육\n"
                        "- 문화예술교육: 음악, 미술, 체육 등 예술 활동\n"
                        "- 인문교양교육: 독서, 역사, 철학 등 교양 강좌\n"
                        "- 시민참여교육: 시민의식, 사회참여 활동\n\n"
                        "주요 기관:\n"
                        "- 장애인 평생교육시설\n"
                        "- 지역 평생학습관\n"
                        "- 대학 부설 평생교육원\n"
                        "- 장애인복지관 평생교육 프로그램\n\n"
                        "평생교육 바우처: 저소득 장애인 대상 연간 35만원 이내 평생교육 비용 지원"
                    ),
                    "source": {
                        "url": "https://www.nile.or.kr",
                        "name": "국가평생교육진흥원",
                        "phone": "02-3780-9700"
                    },
                    "buttons": [
                        {"type": "link", "label": "평생교육 안내", "value": "https://www.nile.or.kr"},
                        {"type": "tel", "label": "국가평생교육진흥원", "value": "02-3780-9700"}
                    ]
                }]
            
            # 최후 방안: 기본 장애인 교육 정보 제공
            return [{
                "id": "education-info-1",
                "title": "장애인 교육 지원 종합 안내",
                "subtitle": "교육 지원",
                "summary": "장애인을 위한 다양한 교육 지원 제도 및 서비스 안내",
                "type": "education",
                "details": (
                    "장애인을 위한 주요 교육 지원 제도 및 서비스 안내입니다.\n\n"
                    "유·초·중등교육:\n"
                    "- 특수교육 지원(특수학교, 특수학급, 통합학급)\n"
                    "- 개별화교육계획(IEP) 수립 및 운영\n"
                    "- 특수교육 관련서비스(치료지원, 보조인력 등)\n"
                    "- 학습보조기기 지원\n\n"
                    "고등·평생교육:\n"
                    "- 장애대학생 교육활동 지원\n"
                    "- 장애인 평생교육 프로그램\n"
                    "- 장애인 정보화교육\n\n"
                    "교육비 지원:\n"
                    "- 특수교육대상자 의무교육 지원\n"
                    "- 장애대학생 장학금 지원\n"
                    "- 평생교육 바우처 지원"
                ),
                "source": {
                    "url": "https://www.nise.go.kr",
                    "name": "국립특수교육원",
                    "phone": "041-537-1500"
                },
                "buttons": [
                    {"type": "link", "label": "자세히 보기", "value": "https://www.nise.go.kr"},
                    {"type": "tel", "label": "국립특수교육원", "value": "041-537-1500"}
                ]
            }]
            
        except Exception as e:
            logger.error(f"교육 정보 검색 중 오류 발생: {e}")
            # 오류 발생 시 기본 데이터 반환
            return [{
                "id": "education-error",
                "title": "장애인 교육 정보 안내",
                "subtitle": "교육 정보",
                "summary": "장애인을 위한 주요 교육 지원 제도 안내",
                "type": "education",
                "details": (
                    "장애인을 위한 다양한 교육 지원 제도가 있습니다:\n"
                    "- 특수교육 지원 제도\n"
                    "- 통합교육 지원\n"
                    "- 개별화교육계획(IEP)\n"
                    "- 교육비 지원 프로그램\n"
                    "- 평생교육 지원\n\n"
                    "자세한 내용은 교육지원청 특수교육지원센터나 국립특수교육원에 문의하세요."
                ),
                "source": {
                    "url": "https://www.nise.go.kr",
                    "name": "국립특수교육원",
                    "phone": "041-537-1500"
                },
                "buttons": [
                    {"type": "link", "label": "교육지원 안내", "value": "https://www.nise.go.kr"},
                    {"type": "tel", "label": "국립특수교육원", "value": "041-537-1500"}
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
            응답 및 교육 정보 카드 정보
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
                        {"role": "system", "content": "사용자의 질문에서 장애인 교육 정보 검색에 필요한 핵심 키워드를 5개 이내로 추출해주세요."},
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
            
            # 교육 정보 검색
            education_cards = await self.search_education_information(keywords)
            
            # 검색 결과 기반 응답 생성
            service_titles = ", ".join([card["title"] for card in education_cards[:3]])
            
            # 대화 이력을 LLM 메시지로 변환
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            
            # 이전 대화 내용이 있으면 메시지에 추가
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if content.strip():  # 내용이 있는 메시지만 추가
                        messages.append({"role": role, "content": content})
            
            # 마지막 질문과 교육 정보 포함
            messages.append({
                "role": "user", 
                "content": f"다음 질문에 대해 관련 교육 정보를 제공해주세요. 관련 서비스: {service_titles}\n\n질문: {query}"
            })
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "cards": education_cards
            }
            
        except Exception as e:
            logger.error(f"교육 전문가 응답 생성 중 오류 발생: {e}")
            return {
                "answer": "죄송합니다. 현재 교육 정보를 제공하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "cards": []
            }
    
    def _get_description(self) -> str:
        return "특수교육, 평생교육, 교육비 지원 정보 제공"
    
    def _get_icon(self) -> str:
        return "🎓"

async def education_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    교육 전문가 응답을 생성합니다.
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 교육 정보 카드 목록
    """
    expert = EducationExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response["answer"], response["cards"] 