from typing import Dict, List, Tuple, Any
import logging
from app.models.expert_type import ExpertType, UserType
from app.service.openai_client import get_client
import json

logger = logging.getLogger(__name__)

class SupervisorAgent:
    """
    슈퍼바이저 AI 에이전트 클래스
    대화 내용을 분석하고, 키워드를 추출하여 적합한 전문가 AI를 선택합니다.
    """
    
    def __init__(self):
        self.client = get_client()
        self.system_prompt = """
        너는 장애인 복지 챗봇 시스템의 슈퍼바이저 AI입니다. 
        사용자의 질문이나 대화 내용을 분석하여 적합한 전문가 AI를 결정하는 역할을 합니다.
        
        장애인 사용자를 위한 전문가:
        - 정책 전문가: 의료, 복지, 취업 관련 정부 정책 정보 제공
        - 취업 전문가: 구직 활동, 직업 교육, 창업 지원 정보 제공
        
        기업 사용자를 위한 전문가:
        - 기업 정책 전문가: 장애인 고용 관련 법률, 지원금 정보 제공
        - 구인 전문가: 장애인 구직자 정보, 채용 절차 안내
        
        입력된 사용자 대화 내용과 사용자 유형을 분석하여 가장 적합한 전문가 AI를 선택하고, 
        관련된 키워드를 추출하여 해당 전문가 AI에게 전달할 수 있도록 준비하세요.
        """
    
    async def analyze_conversation(
        self,
        conversation: List[Dict[str, Any]],
        user_type: UserType
    ) -> Tuple[ExpertType, List[str]]:
        """
        대화 내용을 분석하여 적합한 전문가 유형과 키워드를 추출합니다.
        
        Args:
            conversation: 대화 내용 리스트
            user_type: 사용자 유형
        
        Returns:
            전문가 유형(ExpertType)과 키워드 리스트(List[str])
        """
        try:
            # 대화 내용 요약
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation if msg.get('content')])
            
            # 사용자 유형에 따른 프롬프트 조정
            user_type_prompt = "장애인 사용자" if user_type == UserType.DISABLED else "기업 사용자"
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": f"{self.system_prompt}\n\n현재 사용자는 {user_type_prompt}입니다."},
                    {"role": "user", "content": f"다음 대화 내용을 분석하여 가장 적합한 전문가 유형과 관련 키워드를 추출해주세요:\n\n{conversation_text}"}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            logger.info(f"슈퍼바이저 분석 결과: {result}")
            
            # JSON 파싱
            parsed_result = json.loads(result)
            
            # 전문가 유형과 키워드 추출
            expert_type_str = parsed_result.get("expert_type", "policy")
            keywords = parsed_result.get("keywords", [])
            
            # 문자열을 ExpertType으로 변환
            expert_type = ExpertType(expert_type_str)
            
            return expert_type, keywords
            
        except Exception as e:
            logger.error(f"슈퍼바이저 분석 중 오류 발생: {e}")
            # 사용자 유형에 따른 기본 전문가 선택
            default_expert = ExpertType.POLICY if user_type == UserType.DISABLED else ExpertType.COMPANY_POLICY
            return default_expert, []
    
    async def consolidate_responses(self, expert_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        여러 전문가 AI의 응답을 종합합니다.
        
        Args:
            expert_responses: 전문가 AI 응답 리스트
        
        Returns:
            종합된 응답
        """
        if not expert_responses:
            return {"answer": "현재 이용 가능한 전문가 정보가 없습니다.", "cards": []}
        
        # 단일 전문가 응답인 경우
        if len(expert_responses) == 1:
            return {
                "answer": expert_responses[0].get("answer", ""),
                "cards": expert_responses[0].get("cards", [])
            }
        
        # 여러 전문가 응답 종합
        try:
            # 응답 텍스트와 카드 수집
            all_answers = []
            all_cards = []
            
            for resp in expert_responses:
                if "answer" in resp:
                    all_answers.append(resp["answer"])
                if "cards" in resp:
                    all_cards.extend(resp["cards"])
            
            # 응답 텍스트 종합
            consolidated_text = "\n\n".join(all_answers)
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "여러 전문가의 응답을 자연스럽게 통합하여 하나의 응답으로 만들어주세요. 다음 지침을 따르세요:\n\n1. 항상 따뜻하고 공감적인 톤으로 응답하세요.\n2. 답변 시작 부분에 짧은 공감/위로/격려 멘트를 포함하세요.\n3. 중복된 내용은 제거하고, 모든 중요한 정보를 포함하되 간결하게 정리해주세요.\n4. 정보를 단계별로 또는 카테고리별로 구조화하여 이해하기 쉽게 만들어주세요.\n5. 실용적이고 구체적인 정보와 따뜻한 정서적 지지를 함께 제공하세요."},
                    {"role": "user", "content": f"다음 전문가 응답들을 통합해주세요:\n\n{consolidated_text}"}
                ],
                temperature=0.5
            )
            
            return {
                "answer": response.choices[0].message.content,
                "cards": all_cards
            }
            
        except Exception as e:
            logger.error(f"응답 종합 중 오류 발생: {e}")
            
            # 오류 발생 시 첫 번째 전문가 응답 반환
            if expert_responses:
                return {
                    "answer": expert_responses[0].get("answer", ""),
                    "cards": expert_responses[0].get("cards", [])
                }
            return {
                "answer": "전문가 응답을 처리하는 중 오류가 발생했습니다.",
                "cards": []
            } 