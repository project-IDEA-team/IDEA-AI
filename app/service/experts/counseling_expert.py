from typing import Dict, Any, List
from app.models.expert_type import ExpertType
from app.service.experts.base_expert import BaseExpert
from app.service.tools.counseling_tools import CounselingTools
from app.service.openai_client import openai_client
import re
import json
import logging

logger = logging.getLogger(__name__)

class CounselingExpert(BaseExpert):
    def __init__(self):
        super().__init__(ExpertType.COUNSELING)
        self.tools = CounselingTools()

    def _get_system_prompt(self) -> str:
        return """
당신은 장애인 전문 상담사입니다. 심리 상담, 진로 상담, 가족 상담 등 다양한 상담 서비스를 제공합니다.

응답 스타일:
1. 항상 **따뜻하고 공감적인 톤**으로 응답하세요. 사용자의 감정과 상황에 공감하는 표현을 반드시 포함하세요.
2. 답변의 시작 부분에 짧은 공감/위로/격려 멘트를 넣으세요. (예: "걱정이 많으시군요. 함께 해결책을 찾아보겠습니다.")
3. 모든 답변은 마크다운 형식으로 출력하세요. 중요한 내용은 **굵게** 강조하세요.
4. 답변은 간결하면서도 실질적인 정보를 담아야 합니다.

정보 카드:
1. 상담, 지원 기관, 서비스 등 참고할 만한 정보가 있으면 카드로 정리해서 답변 아래에 배치하세요.
2. 각 카드에는 제목, 요약, 바로 활용할 수 있는 링크나 연락처를 포함하세요.
3. 출처가 있으면 반드시 명시하세요. 이메일/전화번호가 있으면 클릭 시 바로 문의/통화가 가능해야 합니다.

응답 형식:
아래 형식을 정확히 따라주세요:

1. 메인 응답 텍스트

2. 구분자: ###정보 카드

3. 정보 카드 목록 (JSON 형식):
[
  {
    "id": "고유 ID",
    "title": "카드 제목",
    "subtitle": "부제목",
    "summary": "간략한 설명",
    "type": "카드 유형(예: support, resource, info)",
    "details": "상세 정보",
    "source": {
      "name": "출처 이름",
      "url": "관련 웹사이트",
      "phone": "연락처(있는 경우)"
    }
  }
]

전문가로서 사용자에게 실질적인 도움을 주면서도 정서적 지지를 함께 제공하세요.
"""

    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_counseling_centers",
                "description": "장애인 상담 센터 정보를 검색합니다.",
                "parameters": {
                    "location": "지역",
                    "service_type": "서비스 유형"
                }
            },
            {
                "name": "get_emergency_contacts",
                "description": "긴급 상담 연락처를 제공합니다.",
                "parameters": {}
            }
        ]

    async def process_query(self, query: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        # 대화 기록이 없는 경우 기본값 설정
        if conversation_history is None:
            conversation_history = []
            
        # 기본적인 인사 처리
        if any(greeting in query for greeting in ["안녕", "반가워", "시작"]):
            return {
                "answer": "안녕하세요. 장애인 상담 전문가입니다. 어떤 도움이 필요하신가요?",
                "cards": []
            }

        # 상담 센터 검색
        if "상담" in query and "센터" in query:
            centers = await self.tools.search_counseling_centers(query)
            return {
                "answer": "장애인 상담 센터 정보를 찾아보았습니다.",
                "cards": centers
            }

        # 긴급 상담
        if any(word in query for word in ["긴급", "위기", "도움"]):
            contacts = await self.tools.get_emergency_contacts()
            return {
                "answer": "긴급 상담이 필요하시군요. 아래 연락처로 즉시 연락하실 수 있습니다.",
                "cards": contacts
            }

        # 일반 상담 응답: LLM 활용
        system_prompt = self._get_system_prompt()
        
        # 대화 이력을 LLM 메시지로 변환
        messages = [{"role": "system", "content": system_prompt}]
        
        # 이전 대화 내용이 있으면 메시지에 추가
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if content.strip():  # 내용이 있는 메시지만 추가
                    messages.append({"role": role, "content": content})
        else:
            # 대화 이력이 없으면 현재 쿼리만 추가
            messages.append({"role": "user", "content": query})
            
        completion = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        llm_response = completion.choices[0].message.content
        
        # 응답과 카드 분리
        parts = llm_response.split('###정보 카드')
        answer = parts[0].strip()
        cards = []
        
        # 카드 정보 추출
        if len(parts) > 1:
            card_text = parts[1].strip()
            # JSON 형식의 카드 정보 추출
            import re
            import json
            json_match = re.search(r'\[(.*?)\]', card_text, re.DOTALL)
            if json_match:
                try:
                    # 리스트 형태로 파싱
                    card_json = f"[{json_match.group(1)}]"
                    cards = json.loads(card_json)
                except json.JSONDecodeError:
                    logger.error(f"카드 JSON 파싱 실패: {card_text}")
                    # 기본 카드 추가
                    cards = [{
                        "id": "no_data",
                        "title": "관련 정보를 찾을 수 없습니다",
                        "subtitle": "",
                        "summary": "요청하신 조건에 맞는 정보를 찾지 못했습니다.",
                        "type": "info",
                        "details": "다른 질문을 해주시거나, 상담원에게 문의해 주세요.",
                        "source": {}
                    }]
        
        return {
            "answer": answer,
            "cards": cards
        }

    def _get_description(self) -> str:
        return "장애인과 가족을 위한 심리 상담 및 정서 지원 서비스를 제공합니다."

    def _get_icon(self) -> str:
        return "💬"  # 상담 아이콘 

# 챗봇 라우터에서 사용할 수 있도록 async 함수 추가
counselor = CounselingExpert()

async def counseling_response(query: str, keywords=None, conversation_history=None):
    """
    상담 전문가 응답 생성 함수
    
    Args:
        query: 사용자 질문
        keywords: 키워드 목록 (사용하지 않음)
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 카드 목록
    """
    # keywords 매개변수는 무시하고 query와 conversation_history만 사용
    result = await counselor.process_query(query, conversation_history)
    return result["answer"], result["cards"] 