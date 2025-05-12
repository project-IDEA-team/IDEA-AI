from enum import Enum
from typing import Dict, List, Optional, Any
from .nlu import Intent, NLUService
from .mongodb import search_welfare_services, search_disabled_job_offers
from .utils.cache import SimpleCache
from .utils.data_processor import DataProcessor
from .experts import ExpertFactory
from app.models.expert_type import UserType
import logging

logger = logging.getLogger(__name__)

class DialogueState(Enum):
    START = "start"
    AWAITING_SLOTS = "awaiting_slots"
    RESULTS_SHOWN = "results_shown"
    ERROR = "error"

class DialogueManager:
    def __init__(self):
        self.nlu_service = NLUService()
        self.cache = SimpleCache()
        self.data_processor = DataProcessor()
        self.current_expert = None
        self.collected_slots = {}
        
        # 각 의도별 필수 슬롯 정의
        self.required_slots = {
            Intent.EMPLOYMENT: ["region", "disability_type"],
            Intent.POLICY: ["disability_type"],
            Intent.COMPANY_POLICY: ["disability_type", "region"],
            Intent.RECRUITMENT: ["disability_type", "region"],
            Intent.UNKNOWN: []
        }
        
    async def process_message(self, text: str, session_state: Dict[str, Any], user_type: UserType) -> Dict[str, Any]:
        """사용자 메시지를 처리하고 응답을 생성합니다."""
        try:
            # 세션 상태 복원
            self.collected_slots = session_state.get("slots", {})
            self.current_expert = session_state.get("expert_type")
            
            # 의도 분류 (user_type 전달)
            intent, slots = self.nlu_service.classify_and_extract(text, user_type)
            self.collected_slots.update(slots)
            
            # 전문가 결정 (첫 메시지 또는 의도 변경 시에만)
            if not self.current_expert or intent != session_state.get("last_intent"):
                self.current_expert = self._determine_expert_type(intent)
            
            # 필요한 슬롯 확인
            missing_slots = self._get_missing_slots(intent, self.collected_slots)
            
            if missing_slots:
                # 슬롯 수집이 필요한 경우
                next_slot = missing_slots[0]
                response = self._generate_slot_question(next_slot)
                return {
                    "answer": response,
                    "state": DialogueState.AWAITING_SLOTS.value,
                    "slots": self.collected_slots,
                    "expert_type": self.current_expert,
                    "needs_more_info": True,
                    "intent": intent.value
                }
            
            # 전문가 응답 생성
            expert = ExpertFactory.get_expert(self.current_expert)
            if not expert:
                return self._generate_error_response("적절한 전문가를 찾을 수 없습니다.")
            
            try:
                # 캐시된 응답 확인
                cache_key = f"{self.current_expert}:{text}:{str(self.collected_slots)}:{user_type}"
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    cached_response.update({
                        "needs_more_info": False,
                        "intent": intent.value
                    })
                    return cached_response
                
                # 새로운 응답 생성
                response = await expert.process_query(
                    text,
                    user_type,
                    self.collected_slots,
                    session_state.get("conversation_history", [])
                )
                
                # 응답 캐싱
                self.cache.set(cache_key, response)
                
                # 세션 상태 업데이트
                response.update({
                    "state": DialogueState.RESULTS_SHOWN.value,
                    "slots": self.collected_slots,
                    "expert_type": self.current_expert,
                    "needs_more_info": False,
                    "intent": intent.value
                })
                
                return response
                
            except Exception as e:
                logger.exception("응답 생성 중 오류 발생")
                return self._generate_error_response(str(e))
                
        except Exception as e:
            logger.exception("메시지 처리 중 오류 발생")
            return {
                "answer": "죄송합니다. 요청을 처리하는 중 문제가 발생했습니다.",
                "state": DialogueState.ERROR.value,
                "needs_more_info": False,
                "intent": "unknown"
            }
    
    def _determine_expert_type(self, intent: Intent) -> str:
        """의도에 따라 적절한 전문가 유형을 결정합니다."""
        intent_to_expert = {
            Intent.POLICY: "policy",
            Intent.EMPLOYMENT: "employment",
            Intent.COMPANY_POLICY: "company_policy",
            Intent.RECRUITMENT: "recruitment",
            Intent.UNKNOWN: "general"
        }
        return intent_to_expert.get(intent, "general")
    
    def _generate_error_response(self, error_message: str) -> Dict[str, Any]:
        """에러 응답을 생성합니다."""
        return {
            "answer": f"죄송합니다. {error_message}",
            "state": DialogueState.ERROR.value,
            "slots": self.collected_slots,
            "expert_type": self.current_expert,
            "needs_more_info": False,
            "intent": "unknown"
        }
    
    def _get_missing_slots(self, intent: Intent, slots: Dict[str, str]) -> List[str]:
        """필요한 슬롯 중 누락된 항목을 반환합니다."""
        required = self.required_slots.get(intent, [])
        return [slot for slot in required if slot not in slots]
    
    def _generate_slot_question(self, missing_slot: str) -> str:
        """누락된 슬롯 정보를 묻는 질문을 생성합니다."""
        questions = {
            "region": "어느 지역에서 찾아보시겠습니까?",
            "job_type": "어떤 직종에 관심이 있으신가요? (예: 사무, 생산, 서비스, 기술직 등)",
            "disability_type": "어떤 장애 유형에 대해 알아보시겠습니까?"
        }
        return questions.get(missing_slot, "추가 정보가 필요합니다.") 