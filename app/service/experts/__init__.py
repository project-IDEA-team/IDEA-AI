from typing import Dict, List, Tuple, Any, Optional
import logging
from app.models.expert_type import ExpertType
from app.service.experts.policy_expert import policy_response
from app.service.experts.employment_expert import employment_response
from app.service.experts.welfare_expert import welfare_response
from app.service.experts.startup_expert import startup_response
from app.service.experts.medical_expert import medical_response
from app.service.experts.education_expert import education_response
from app.service.experts.counseling_expert import counseling_response

logger = logging.getLogger(__name__)

# 전문가 유형별 응답 함수 매핑
expert_responses = {
    "정책": policy_response,
    "장애인 정책": policy_response,
    "취업": employment_response,
    "장애인 취업": employment_response,
    "복지": welfare_response,
    "장애인 복지": welfare_response,
    "창업": startup_response,
    "장애인 창업": startup_response,
    "의료": medical_response,
    "장애인 의료": medical_response,
    "교육": education_response,
    "장애인 교육": education_response,
    "상담": counseling_response,
    "전문 상담": counseling_response
}

# 전문가 유형 이름 매핑 (ExpertType enum과 한글 이름 매핑)
expert_type_names = {
    ExpertType.POLICY: "정책",
    ExpertType.EMPLOYMENT: "취업",
    ExpertType.WELFARE: "복지",
    ExpertType.STARTUP: "창업",
    ExpertType.MEDICAL: "의료",
    ExpertType.EDUCATION: "교육",
    ExpertType.COUNSELING: "상담"
}

# 한글 이름으로 ExpertType 찾기
expert_names_to_type = {v: k for k, v in expert_type_names.items()}
# 프론트엔드에서 사용하는 전문가 유형도 매핑에 추가
expert_names_to_type.update({
    "장애인 정책": ExpertType.POLICY,
    "장애인 취업": ExpertType.EMPLOYMENT,
    "장애인 복지": ExpertType.WELFARE,
    "장애인 창업": ExpertType.STARTUP,
    "장애인 의료": ExpertType.MEDICAL,
    "장애인 교육": ExpertType.EDUCATION,
    "전문 상담": ExpertType.COUNSELING
})

async def get_expert_response(query: str, expert_type: str, keywords: List[str] = None, conversation_history=None) -> Tuple[str, List[Dict[str, Any]]]:
    """
    전문가 유형에 따라 적절한 전문가 응답 함수를 호출하여 응답을 생성합니다.
    
    Args:
        query: 사용자 쿼리
        expert_type: 전문가 유형 ("정책", "취업", "복지", "창업", "의료", "교육", "상담" 중 하나)
        keywords: 슈퍼바이저가 추출한 키워드 목록
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 관련 정보 카드 목록
    """
    try:
        logger.info(f"전문가 유형 '{expert_type}'에 대한 응답 생성 시작")
        
        # 전문가 응답 함수 선택
        response_func = expert_responses.get(expert_type)
        
        if response_func is None:
            logger.error(f"존재하지 않는 전문가 유형: {expert_type}")
            return "죄송합니다. 해당 분야의 전문가를 찾을 수 없습니다.", []
        
        # 키워드가 없는 경우 빈 리스트로 초기화
        if keywords is None:
            keywords = []
        
        # 전문가 응답 함수 호출
        logger.debug(f"'{expert_type}' 전문가 응답 함수 호출: 키워드={keywords}")
        answer, cards = await response_func(query, keywords, conversation_history)
        
        logger.info(f"전문가 응답 생성 완료: {len(cards)}개의 카드 생성됨")
        return answer, cards
        
    except Exception as e:
        logger.error(f"전문가 응답 생성 중 오류 발생: {e}", exc_info=True)
        return "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.", []

def get_available_experts() -> List[Dict[str, Any]]:
    """
    사용 가능한 모든 전문가 정보를 반환합니다.
    
    Returns:
        전문가 정보 목록
    """
    from app.service.experts.policy_expert import PolicyExpert
    from app.service.experts.employment_expert import EmploymentExpert
    from app.service.experts.welfare_expert import WelfareExpert
    from app.service.experts.startup_expert import StartupExpert
    from app.service.experts.medical_expert import MedicalExpert
    from app.service.experts.education_expert import EducationExpert
    from app.service.experts.counseling_expert import CounselingExpert
    
    experts = [
        PolicyExpert(),
        EmploymentExpert(),
        WelfareExpert(),
        StartupExpert(),
        MedicalExpert(),
        EducationExpert(),
        CounselingExpert()
    ]
    
    return [
        {
            "id": expert.expert_type.value,
            "name": expert_type_names[expert.expert_type],
            "description": expert._get_description(),
            "icon": expert._get_icon()
        }
        for expert in experts
    ]

def get_expert_by_name(name: str) -> Optional[ExpertType]:
    """
    전문가 이름으로 ExpertType을 찾습니다.
    
    Args:
        name: 전문가 이름 (한글)
        
    Returns:
        ExpertType 또는 None (존재하지 않는 경우)
    """
    return expert_names_to_type.get(name) 