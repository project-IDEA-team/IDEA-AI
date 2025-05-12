from typing import Dict, List, Any
import logging
from app.service.openai_client import get_client
from app.models.expert_type import ExpertType, UserType
from app.service.experts import Expert

logger = logging.getLogger(__name__)

class GeneralChatbot:
    """
    일반 챗봇 AI 클래스
    사용자와의 대화를 처리하고, 응답을 생성합니다.
    전문가 AI의 응답을 사용자 친화적으로 가공하는 역할도 담당합니다.
    """
    
    def __init__(self):
        self.client = get_client()
        self.system_prompt = """
        너는 장애인 복지 정보를 제공하는 친절한 AI 챗봇입니다. 
        사용자의 질문에 정확하고 공감적으로 응답해야 합니다.
        
        응답 원칙:
        1. 항상 따뜻하고 공감적인 톤으로 응답하세요. 사용자의 감정과 상황에 대한 이해를 표현하세요.
        2. 답변 시작 부분에 짧은 공감/위로/격려 멘트를 포함하세요.
        3. 간결하면서도 실질적인 정보를 제공하세요. 중요한 부분은 강조하여 안내하세요.
        4. 장애인과 그 가족들에게 도움이 되는 구체적이고 실용적인 정보를 제공하세요.
        5. 복잡한 정책이나 제도를 쉽게 설명하되, 정확성을 유지하세요.
        6. 필요한 경우 추가 질문을 통해 사용자의 요구를 정확히 파악하세요.
        7. 모르는 내용은 정직하게 모른다고 답하고, 관련 기관이나 전문가에게 문의할 것을 권유하세요.
        
        정보 카드 활용:
        1. 유용한 정보는 본문 응답 아래에 정보 카드 형태로 제공하세요.
        2. 카드에는 제목, 요약, 연락처나 링크 등 즉시 활용 가능한 정보를 포함하세요.
        3. 출처가 있는 정보는 반드시 출처를 명시하세요.
        
        사용자가 정보를 쉽게 이해하고, 정서적으로도 지지받는다고 느낄 수 있도록 응답하세요.
        """
    
    async def process_initial_query(self, query: str, user_type: UserType) -> Dict[str, Any]:
        """
        사용자의 초기 질문을 처리합니다.
        
        Args:
            query: 사용자 질문
            user_type: 사용자 유형
        
        Returns:
            초기 응답과 대화 요약
        """
        try:
            # 기본 전문가 선택 (사용자 유형에 따라)
            expert_type = ExpertType.POLICY if user_type == UserType.DISABLED else ExpertType.COMPANY_POLICY
            expert = Expert(expert_type)
            
            # 전문가 응답 생성
            response = await expert.process_query(query, user_type, {})
            
            # 대화 요약 생성
            summary_response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "사용자의 질문을 간결하게 요약하고, 핵심 의도를 파악해주세요."},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            conversation_summary = summary_response.choices[0].message.content
            
            return {
                "answer": response["answer"],
                "cards": response["cards"],
                "conversation_summary": conversation_summary
            }
            
        except Exception as e:
            logger.error(f"초기 질문 처리 중 오류 발생: {e}")
            return {
                "answer": "죄송합니다. 현재 요청을 처리할 수 없습니다. 잠시 후 다시 시도해주세요.",
                "cards": [],
                "conversation_summary": query
            }
    
    async def create_user_friendly_response(
        self,
        expert_response: Dict[str, Any],
        conversation: List[Dict[str, str]],
        user_type: UserType
    ) -> Dict[str, Any]:
        """
        전문가 AI의 응답을 사용자 친화적인 형태로 가공합니다.
        
        Args:
            expert_response: 전문가 AI의 응답
            conversation: 이전 대화 내용
            user_type: 사용자 유형
        
        Returns:
            사용자 친화적인 응답
        """
        try:
            # 전문가 응답과 이전 대화 내용 결합
            expert_answer = expert_response.get("answer", "")
            
            # 딕셔너리 형태의 대화 내용 사용
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation[-3:]
                if msg.get('content')
            ])
            
            # 사용자 유형에 따른 프롬프트 조정
            user_type_prompt = "장애인 사용자" if user_type == UserType.DISABLED else "기업 사용자"
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": f"{self.system_prompt}\n\n현재 사용자는 {user_type_prompt}입니다."},
                    {"role": "user", "content": f"이전 대화:\n{conversation_text}\n\n전문가 응답:\n{expert_answer}"}
                ],
                temperature=0.7
            )
            
            return {
                "answer": response.choices[0].message.content,
                "cards": expert_response.get("cards", [])
            }
            
        except Exception as e:
            logger.error(f"응답 가공 중 오류 발생: {e}")
            return {
                "answer": expert_response.get("answer", "죄송합니다. 응답을 처리하는 중 오류가 발생했습니다."),
                "cards": expert_response.get("cards", [])
            } 