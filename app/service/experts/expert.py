from typing import Dict, List, Any, Optional
import logging
from app.models.expert_type import ExpertType, UserType
from app.service.openai_client import get_client
from app.service.mongodb import search_chunks_by_keyword, search_welfare_services, search_disabled_job_offers

logger = logging.getLogger(__name__)

class Expert:
    """통합된 전문가 AI 클래스"""
    
    def __init__(self, expert_type: ExpertType):
        self.expert_type = expert_type
        self.client = get_client()
        
        # 전문가 유형별 시스템 프롬프트
        self.system_prompts = {
            ExpertType.POLICY: """
            당신은 장애인 정책 전문가입니다.
            의료, 복지, 취업 관련 정부 정책에 대한 전문적인 지식을 가지고 있습니다.
            사용자의 질문에 대해 관련 정책과 지원 제도를 안내해주세요.
            """,
            ExpertType.EMPLOYMENT: """
            당신은 장애인 취업/창업 전문가입니다.
            구인 정보, 취업 교육, 훈련 프로그램, 창업 지원에 대한 전문적인 지식을 가지고 있습니다.
            사용자의 상황에 맞는 취업/창업 정보를 제공해주세요.
            """,
            ExpertType.COMPANY_POLICY: """
            당신은 기업 정책 전문가입니다.
            장애인 고용 관련 법률, 의무고용, 지원금 제도에 대한 전문적인 지식을 가지고 있습니다.
            기업의 장애인 고용과 관련된 문의에 답변해주세요.
            """,
            ExpertType.RECRUITMENT: """
            당신은 장애인 채용 전문가입니다.
            장애인 구직자 정보 제공과 기업 맞춤형 인재 추천을 담당합니다.
            기업의 채용 needs에 맞는 인재 정보를 제공해주세요.
            """
        }
    
    async def process_query(
        self,
        query: str,
        user_type: UserType,
        slots: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        사용자 질의를 처리하고 응답을 생성합니다.
        
        Args:
            query: 사용자 질문
            user_type: 사용자 유형
            slots: 추출된 슬롯 정보
            conversation_history: 이전 대화 내용
            
        Returns:
            응답 딕셔너리 (answer, cards)
        """
        try:
            # 1. 관련 정보 검색
            info_cards = await self._generate_info_cards(query, user_type, slots)
            
            # 2. 컨텍스트 구성
            context = self._build_context(query, slots, info_cards)
            
            # 3. GPT 응답 생성
            messages = [
                {"role": "system", "content": self.system_prompts[self.expert_type]},
                {"role": "user", "content": context}
            ]
            
            if conversation_history:
                # 최근 3개 메시지만 포함
                for msg in conversation_history[-3:]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7
            )
            
            return {
                "answer": response.choices[0].message.content,
                "cards": info_cards
            }
            
        except Exception as e:
            logger.error(f"전문가 응답 생성 중 오류 발생: {e}")
            return {
                "answer": "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다.",
                "cards": []
            }
    
    async def _generate_info_cards(
        self,
        query: str,
        user_type: UserType,
        slots: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """관련 정보 카드를 생성합니다."""
        cards = []
        
        try:
            if user_type == UserType.DISABLED:
                if self.expert_type == ExpertType.POLICY:
                    # 정책 정보 검색
                    policy_results = search_chunks_by_keyword(query)
                    welfare_results = search_welfare_services(query)
                    
                    # 정책 카드 생성
                    for result in policy_results:
                        cards.append({
                            "id": str(result["_id"]),
                            "title": result["metadata"]["title"],
                            "summary": result["page_content"][:100],
                            "type": "policy",
                            "details": result["page_content"]
                        })
                    
                    # 복지 서비스 카드 생성
                    for service in welfare_results:
                        cards.append({
                            "id": service["servId"],
                            "title": service["servNm"],
                            "summary": service["servDgst"],
                            "type": "welfare",
                            "details": service.get("servDtlCn", "")
                        })
                
                elif self.expert_type == ExpertType.EMPLOYMENT:
                    # 구직 정보 검색
                    job_results = search_disabled_job_offers(query)
                    
                    # 구직 카드 생성
                    for job in job_results:
                        cards.append({
                            "id": str(job["_id"]),
                            "title": job["title"],
                            "summary": f"{job['location']} / {job['company']}",
                            "type": "employment",
                            "details": job.get("description", "")
                        })
            
            else:  # UserType.COMPANY
                if self.expert_type == ExpertType.COMPANY_POLICY:
                    # 기업 정책 검색
                    policy_results = search_chunks_by_keyword("장애인 고용 의무")
                    
                    # 정책 카드 생성
                    for result in policy_results:
                        cards.append({
                            "id": str(result["_id"]),
                            "title": result["metadata"]["title"],
                            "summary": result["page_content"][:100],
                            "type": "company_policy",
                            "details": result["page_content"]
                        })
                
                elif self.expert_type == ExpertType.RECRUITMENT:
                    # 구직자 정보 검색
                    candidates = search_disabled_job_offers()
                    
                    # 구직자 카드 생성
                    for candidate in candidates:
                        cards.append({
                            "id": str(candidate["_id"]),
                            "title": f"{candidate['job_type']} ({candidate['disability_type']})",
                            "summary": f"{candidate['location']} / {candidate['experience']}",
                            "type": "recruitment",
                            "details": candidate.get("details", "")
                        })
        
        except Exception as e:
            logger.error(f"정보 카드 생성 중 오류 발생: {e}")
        
        return cards
    
    def _build_context(
        self,
        query: str,
        slots: Dict[str, Any],
        info_cards: List[Dict[str, Any]]
    ) -> str:
        """GPT 응답 생성을 위한 컨텍스트를 구성합니다."""
        context = f"사용자 질문: {query}\n\n"
        
        if slots:
            context += "추출된 정보:\n"
            for key, value in slots.items():
                context += f"- {key}: {value}\n"
            context += "\n"
        
        if info_cards:
            context += "관련 정보:\n"
            for card in info_cards:
                context += f"- {card['title']}: {card['summary']}\n"
        
        return context 