from typing import Dict, List, Any
import logging
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.openai_client import get_client

logger = logging.getLogger(__name__)

class MedicalExpert(BaseExpert):
    """
    의료 전문가 AI 클래스
    장애인 의료 지원, 재활 서비스, 건강 정보 등을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(ExpertType.MEDICAL)
        self.client = get_client()
        self.model = "gpt-4.1-mini"
    
    def _get_system_prompt(self) -> str:
        return """
        너는 장애인 의료 전문가 AI입니다. 
        장애인 의료 지원 제도, 재활 서비스, 건강 관리 정보 등에 대한 정확하고 유용한 정보를 제공해야 합니다.
        
        제공할 정보 범위:
        - 장애인 의료비 지원 제도
        - 장애인 건강검진 지원
        - 장애인 재활 치료 및 서비스
        - 보조기기 지원 및 활용
        - 장애유형별 건강관리 정보
        - 장애인 진료기관 및 전문 의료서비스
        - 정신건강 지원 서비스
        
        응답 스타일:
        1. 항상 따뜻하고 공감적인 톤으로 응답하세요. 건강 문제에 대한 우려와 불안을 이해하는 표현을 포함하세요.
        2. 응답 시작 부분에 짧은 공감/안심 멘트를 추가하세요. (예: "건강 문제로 걱정이 많으시겠네요. 도움이 될 정보를 알려드리겠습니다.")
        3. 의학 정보를 정확하되 쉽게 설명하며, 전문용어는 가능한 풀어서 설명하세요.
        4. 의료 지원 제도의 신청 방법, 자격 조건, 혜택 내용을 구체적으로 안내하세요.
        5. 장애 유형별로 특화된 건강 관리 정보를 제공하되, 개인 상황에 따라 차이가 있을 수 있음을 안내하세요.
        6. 의학적 조언은 참고용이며, 반드시 의사와 상담할 것을 권고하세요.
        
        정보 카드:
        1. 모든 응답에는 반드시 관련 의료 정보 카드를 포함하세요.
        2. 카드에는 의료 지원 제도, 재활 서비스, 전문 의료기관 등 핵심 정보를 담으세요.
        
        사용자의 건강 향상에 도움이 되는 실질적인 정보를 제공하면서도, 건강에 대한 걱정을 공감하고 안심시키는 응답을 제공하세요.
        """
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_medical_information",
                    "description": "장애인 의료 정보를 검색합니다.",
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
                            "medical_type": {
                                "type": "string",
                                "description": "의료 서비스 유형"
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
    
    async def search_medical_information(self, keywords: List[str], medical_type: str = None, disability_type: str = None, region: str = None) -> List[Dict[str, Any]]:
        """
        키워드, 의료 서비스 유형, 장애 유형, 지역 등을 기반으로 의료 정보를 검색합니다.
        API 호출 대신 기본 데이터를 반환합니다.
        
        Args:
            keywords: 검색 키워드 목록
            medical_type: 의료 서비스 유형
            disability_type: 장애 유형
            region: 지역 정보
            
        Returns:
            검색된 의료 정보 카드 목록
        """
        # 의료비 지원 관련 키워드가 있으면 의료비 지원 정보 제공
        if any(kw in ["의료비", "진료비", "병원비", "비용", "지원금"] for kw in keywords):
            return [{
                "id": "medical-cost-1",
                "title": "장애인 의료비 지원사업",
                "subtitle": "의료비 지원",
                "summary": "저소득 장애인의 의료비 부담 경감을 위한 지원 제도",
                "type": "medical",
                "details": (
                    "장애인 의료비 지원사업은 저소득 장애인의 의료비 부담을 덜어주기 위한 제도입니다.\n\n"
                    "지원대상:\n"
                    "- 의료급여법에 의한 의료급여 2종 수급권자인 등록장애인\n"
                    "- 건강보험의 차상위 본인부담경감대상자인 등록장애인\n\n"
                    "지원내용:\n"
                    "- 의료기관 이용 시 발생하는 본인부담금 지원\n"
                    "- 1차 의료기관: 외래 750원 본인부담\n"
                    "- 2차, 3차 의료기관: 본인부담금의 약 14~15% 본인부담\n"
                    "- 비급여 항목은 지원 제외\n\n"
                    "신청방법: 별도 신청 필요 없이 의료기관 이용 시 자격 확인 후 자동 적용"
                ),
                "source": {
                    "url": "https://www.bokjiro.go.kr",
                    "name": "복지로",
                    "phone": "129"
                },
                "buttons": [
                    {"type": "link", "label": "제도 안내", "value": "https://www.bokjiro.go.kr/medical-support"},
                    {"type": "tel", "label": "보건복지상담센터", "value": "129"}
                ]
            }]
        
        # 재활 관련 키워드가 있으면 재활 서비스 정보 제공
        if any(kw in ["재활", "치료", "물리", "작업치료", "언어치료"] for kw in keywords):
            return [{
                "id": "rehabilitation-1",
                "title": "장애인 재활치료 서비스",
                "subtitle": "재활치료",
                "summary": "장애인의 기능 회복과 유지를 위한 다양한 재활치료 서비스",
                "type": "medical",
                "details": (
                    "장애인 재활치료 서비스는 장애인의 신체적, 정신적 기능 회복과 유지를 돕는 서비스입니다.\n\n"
                    "제공 서비스:\n"
                    "- 물리치료: 관절 운동, 근력 강화, 통증 관리 등\n"
                    "- 작업치료: 일상생활 기술 훈련, 인지 재활 등\n"
                    "- 언어치료: 의사소통 능력 향상, 발음 교정 등\n"
                    "- 보조기기 훈련: 맞춤형 보조기기 사용법 교육\n"
                    "- 심리재활: 장애 수용 및 적응 상담\n\n"
                    "이용방법:\n"
                    "- 지역 재활병원 및 장애인복지관 방문 신청\n"
                    "- 국민건강보험공단 재활치료 이용 신청\n\n"
                    "비용지원: 건강보험, 의료급여, 장애인 의료비 지원사업 등을 통해 일부 본인부담금 경감"
                ),
                "source": {
                    "url": "https://www.nrc.go.kr",
                    "name": "국립재활원",
                    "phone": "02-901-1700"
                },
                "buttons": [
                    {"type": "link", "label": "서비스 안내", "value": "https://www.nrc.go.kr"},
                    {"type": "tel", "label": "국립재활원", "value": "02-901-1700"}
                ]
            }]
        
        # 보조기기 관련 키워드가 있으면 보조기기 정보 제공
        if any(kw in ["보조기기", "보조기구", "복지용구", "휠체어", "보장구"] for kw in keywords):
            return [{
                "id": "assistive-device-1",
                "title": "장애인 보조기기 지원사업",
                "subtitle": "보조기기 지원",
                "summary": "일상생활 및 재활에 필요한 보조기기 구입 비용 지원",
                "type": "medical",
                "details": (
                    "장애인 보조기기 지원사업은 장애인의 일상생활과 재활에 필요한 보조기기 구입 비용을 지원하는 제도입니다.\n\n"
                    "지원대상:\n"
                    "- 국민기초생활보장법상 수급자 및 차상위계층 등록 장애인\n"
                    "- 지원품목에 따라 장애유형과 등급 기준 상이\n\n"
                    "지원품목:\n"
                    "- 이동보조기기: 휠체어, 보행보조기 등\n"
                    "- 일상생활보조기기: 목욕의자, 식사보조기기 등\n"
                    "- 의사소통보조기기: 독서확대기, 영상확대비디오 등\n"
                    "- 정보접근보조기기: 특수마우스, 특수키보드 등\n\n"
                    "지원금액: 품목별 기준액 범위 내 실제 구입가격 지원\n\n"
                    "신청방법: 주소지 관할 읍·면·동 주민센터 신청"
                ),
                "source": {
                    "url": "https://www.knat.go.kr",
                    "name": "국립재활원 중앙보조기기센터",
                    "phone": "1670-5529"
                },
                "buttons": [
                    {"type": "link", "label": "보조기기 안내", "value": "https://www.knat.go.kr"},
                    {"type": "tel", "label": "중앙보조기기센터", "value": "1670-5529"}
                ]
            }]
        
        # 기본 장애인 건강 및 의료 정보 제공
        return [{
            "id": "medical-info-1",
            "title": "장애인 건강 및 의료 지원 안내",
            "subtitle": "의료 지원",
            "summary": "장애인을 위한 건강관리 및 의료지원 서비스 종합 안내",
            "type": "medical",
            "details": (
                "장애인을 위한 주요 의료 지원 서비스 안내입니다.\n\n"
                "의료비 지원:\n"
                "- 장애인 의료비 지원사업\n"
                "- 건강보험 본인부담금 경감제도\n"
                "- 희귀난치성질환자 의료비 지원\n\n"
                "재활 서비스:\n"
                "- 지역사회중심재활사업\n"
                "- 장애인 건강검진 지원\n"
                "- 발달재활 서비스\n\n"
                "보조기기 지원:\n"
                "- 장애인보조기기 구입비 지원\n"
                "- 보조기기 대여 및 수리 지원\n\n"
                "의료기관 이용:\n"
                "- 장애인 건강주치의 제도\n"
                "- 장애인 건강보건관리 서비스"
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
            
            # 기본 의료 정보 카드 
            medical_cards = [{
                "id": "medical-info-general",
                "title": "장애인 의료 지원 정보",
                "subtitle": "의료 지원",
                "summary": "장애인을 위한 주요 의료 지원 제도 안내",
                "type": "medical",
                "details": (
                    "장애인을 위한 주요 의료 지원 제도:\n\n"
                    "1. 장애인 의료비 지원사업\n"
                    "- 의료급여 2종 수급권자, 차상위 본인부담경감대상자인 등록장애인 대상\n"
                    "- 의료기관 이용 시 본인부담금 일부 지원\n"
                    "- 문의: 보건복지상담센터 129\n\n"
                    "2. 장애인 건강주치의 제도\n"
                    "- 만성질환 등 건강관리가 필요한 장애인에게 주치의 서비스 제공\n"
                    "- 문의: 국민건강보험공단 1577-1000\n\n"
                    "3. 발달재활서비스\n"
                    "- 만 18세 미만 장애아동에게 언어, 청능, 미술, 음악, 행동, 놀이, 심리운동, 재활심리, 감각통합, 운동재활 등 서비스 제공\n"
                    "- 문의: 주소지 읍면동 주민센터"
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
                "cards": medical_cards
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
        return "장애인 의료 지원, 재활 서비스, 건강 정보 등에 대한 정보를 제공합니다."
    
    def _get_icon(self) -> str:
        return "🏥"

async def medical_response(query: str, keywords: List[str] = None, conversation_history=None) -> tuple:
    """
    의료 전문가 AI 응답 생성 함수
    
    Args:
        query: 사용자 쿼리
        keywords: 키워드 목록
        conversation_history: 대화 이력
        
    Returns:
        (응답 텍스트, 정보 카드 목록)
    """
    expert = MedicalExpert()
    response = await expert.process_query(query, keywords, conversation_history)
    return response.get("text", ""), response.get("cards", []) 