from typing import Dict, List, Tuple, Any
import logging
from app.models.expert_type import ExpertType
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
        각 전문가 AI 유형과 그 역할은 다음과 같습니다:
        
        - 정책: 장애인 관련 법률, 제도, 정책 등에 대한 정보 제공
        - 취업: 장애인 취업 정보, 구직 활동 지원, 직업 훈련 등 정보 제공
        - 복지: 장애인 복지 서비스, 혜택 등에 대한 정보 제공
        - 창업: 장애인 창업 지원, 창업 교육, 자금 지원 등 정보 제공
        - 의료: 장애인 의료 지원, 재활 치료, 건강 관리 등 정보 제공
        - 교육: 장애인 교육 프로그램, 학습 지원, 특수 교육 등 정보 제공
        - 상담: 장애인과 가족의 심리, 정서적 고충에 대한 상담 제공
        
        입력된 사용자 대화 내용을 분석하여 가장 적합한 전문가 AI를 선택하고, 
        관련된 키워드를 추출하여 해당 전문가 AI에게 전달할 수 있도록 준비하세요.
        """
    
    async def analyze_conversation(self, conversation: List[Dict[str, Any]]) -> Tuple[ExpertType, List[str]]:
        """
        대화 내용을 분석하여 적합한 전문가 유형과 키워드를 추출합니다.
        
        Args:
            conversation: 대화 내용 리스트
        
        Returns:
            전문가 유형(ExpertType)과 키워드 리스트(List[str])
        """
        try:
            # 대화 내용 요약
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation if msg.get('content')])
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"다음 대화 내용을 분석하여 가장 적합한 전문가 유형과 관련 키워드를 추출해주세요:\n\n{conversation_text}"}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            logger.info(f"슈퍼바이저 분석 결과: {result}")
            
            # JSON 파싱
            parsed_result = json.loads(result)
            
            # 전문가 유형과 키워드 추출
            expert_type_str = parsed_result.get("expert_type", "상담")
            keywords = parsed_result.get("keywords", [])
            
            # 문자열을 ExpertType으로 변환
            expert_type = None
            for et in ExpertType:
                if et.value == expert_type_str:
                    expert_type = et
                    break
            
            # 기본값: 상담 전문가
            if expert_type is None:
                expert_type = ExpertType.COUNSELING
            
            # 장애인 구직자 관련 데이터 요청 처리 (고정 데이터 반환)
            latest_message = conversation[-1]["content"] if conversation else ""
            if any(keyword in latest_message for keyword in ["장애인 구직자", "구직자 현황", "구직자 통계"]):
                # 고정된 샘플 데이터
                cards = [
                    {
                        "id": "1",
                        "title": "사무직 (지체장애)",
                        "summary": "서울 / 중증",
                        "details": "연령: 30대, 희망임금: 월 200만원 이상, 등록일: 2023-09-15"
                    },
                    {
                        "id": "2",
                        "title": "IT/프로그래머 (시각장애)",
                        "summary": "경기 / 중증",
                        "details": "연령: 20대, 희망임금: 월 250만원 이상, 등록일: 2023-10-01"
                    },
                    {
                        "id": "3",
                        "title": "콜센터 (청각장애)",
                        "summary": "인천 / 경증",
                        "details": "연령: 40대, 희망임금: 월 180만원 이상, 등록일: 2023-10-10"
                    }
                ]
                return "장애인 구직자 현황 정보입니다.", cards
            
            return expert_type, keywords
            
        except Exception as e:
            logger.error(f"슈퍼바이저 분석 중 오류 발생: {e}")
            return ExpertType.COUNSELING, []
    
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
            expert_response = expert_responses[0]
            
            # 기존 응답 형식 유지하면서 text/cards 키도 지원
            result = {
                "answer": expert_response.get("answer", expert_response.get("text", "")),
                "cards": expert_response.get("cards", [])
            }
            
            # text/cards 키 추가 (호환성 유지)
            if "answer" in expert_response and "text" not in expert_response:
                result["text"] = expert_response["answer"]
            
            # action 필드가 있으면 포함
            if "action" in expert_response:
                result["action"] = expert_response["action"]
            
            return result
        
        # 여러 전문가 응답 종합
        try:
            # 응답 텍스트와 카드 수집
            all_answers = []
            action_field = None
            for resp in expert_responses:
                if "answer" in resp:
                    all_answers.append(resp["answer"])
                elif "text" in resp:
                    all_answers.append(resp["text"])
                # action 필드가 있는 첫 번째 응답의 action을 저장
                if not action_field and "action" in resp:
                    action_field = resp["action"]
            
            all_cards = []
            for resp in expert_responses:
                if resp.get("cards"):
                    all_cards.extend(resp.get("cards"))
            
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
            
            consolidated_answer = response.choices[0].message.content
            
            result = {
                "answer": consolidated_answer,
                "text": consolidated_answer,  # 새로운 키 형식 지원
                "cards": all_cards
            }
            # action 필드가 있으면 포함
            if action_field:
                result["action"] = action_field
            return result
            
        except Exception as e:
            logger.error(f"응답 종합 중 오류 발생: {e}")
            
            # 오류 발생 시 첫 번째 전문가 응답 반환
            if expert_responses:
                expert_response = expert_responses[0]
                answer = expert_response.get("answer", expert_response.get("text", ""))
                return {
                    "answer": answer,
                    "text": answer,
                    "cards": expert_response.get("cards", [])
                }
            return {
                "answer": "전문가 응답을 처리하는 중 오류가 발생했습니다.",
                "text": "전문가 응답을 처리하는 중 오류가 발생했습니다.",
                "cards": []
            } 