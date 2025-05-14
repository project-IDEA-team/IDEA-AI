from typing import Dict, List, Tuple, Any, Optional
import logging
from app.models.expert_type import ExpertType
from app.service.experts.policy_expert import policy_response, PolicyExpert

logger = logging.getLogger(__name__)

# 전문가 유형별 응답 함수 매핑 
expert_responses = {
    ExpertType.POLICY.value: policy_response,
    "장애인 정책": policy_response,
    ExpertType.EMPLOYMENT.value: policy_response,
    "취업": policy_response,

    #기업회원용 전문가 타입 매핑
    ExpertType.EMPLOYMENT_POLICY.value: policy_response,
    "고용 정책": policy_response,
    ExpertType.JOB_SEEKERS.value: policy_response,
    
    
}

# 전문가 유형별 클래스 매핑 
expert_classes = {
    ExpertType.POLICY.value: PolicyExpert,
    "장애인 정책": PolicyExpert,
    ExpertType.EMPLOYMENT.value: PolicyExpert,
    "취업": PolicyExpert,

    #기업회원용 전문가 타입 매핑
    ExpertType.EMPLOYMENT_POLICY.value: PolicyExpert,
    "고용 정책": PolicyExpert,
    ExpertType.JOB_SEEKERS.value: PolicyExpert,
    "구직자 현황": PolicyExpert,
}

# 전문가 유형 이름 매핑 (ExpertType enum과 한글 이름 매핑 - 정책 전문가만 남김)
expert_type_names = {
    ExpertType.POLICY: "정책",
    ExpertType.EMPLOYMENT: "취업",
    # ExpertType.WELFARE: "복지",
    # ExpertType.STARTUP: "창업",
    # ExpertType.MEDICAL: "의료",
    # ExpertType.EDUCATION: "교육",
    # ExpertType.COUNSELING: "상담",
    # 기업회원용 전문가 타입 매핑 (MVP에서 제외)
    ExpertType.EMPLOYMENT_POLICY: "고용 정책",
    ExpertType.JOB_SEEKERS: "구직자 현황",
    # ExpertType.CONSULTING: "고용 컨설팅",
    # ExpertType.APPLICATION_MANAGE: "지원의향서"
}

# 한글 이름으로 ExpertType 찾기 (정책 전문가만 남김)
expert_names_to_type = {v: k for k, v in expert_type_names.items()}
# 프론트엔드에서 사용하는 전문가 유형도 매핑에 추가 (정책 전문가만 남김)
expert_names_to_type.update({
    "장애인 정책": ExpertType.POLICY,
    "취업": ExpertType.EMPLOYMENT,
    # 기업회원용 전문가 타입 매핑 
    "고용 정책": ExpertType.EMPLOYMENT_POLICY,
    "구직자 현황": ExpertType.JOB_SEEKERS,
    
})

async def get_expert_response(query: str, expert_type: str, keywords: List[str] = None, conversation_history=None) -> Tuple[str, List[Dict[str, Any]], Optional[str]]:
    """
    전문가 유형에 따라 적절한 전문가 응답 함수를 호출하여 응답을 생성합니다.
    
    Args:
        query: 사용자 쿼리
        expert_type: 전문가 유형
        keywords: 슈퍼바이저가 추출한 키워드 목록
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트, 관련 정보 카드 목록, 추가 액션 (예: "view_employment_detail")
    """
    try:
        # expert_classes에서 직접 expert_type.value를 사용하여 전문가 클래스를 가져옵니다.
        expert_class = expert_classes.get(expert_type)
        # 만약 expert_type이 MVP에 포함되지 않은 전문가 유형이라면, expert_class는 None이 됩니다.
        
        expert_class_name = expert_class.__name__ if expert_class else "Unknown"
        logger.info(f"전문가 유형 '{expert_type}' ({expert_class_name})에 대한 응답 생성 시작 - 쿼리: '{query[:100]}...' if len(query) > 100 else query")
        
        # 키워드가 없는 경우 빈 리스트로 초기화
        if keywords is None:
            keywords = []
            # 간단한 키워드 추출 (쿼리에서 주요 단어 추출)
            words = query.replace("?", "").replace(".", "").replace(",", "").split()
            keywords = [w for w in words if len(w) > 1 and w not in ["저는", "나는", "제가", "그런데", "그리고", "하지만", "어떻게", "어떤", "무엇", "왜"]]
            keywords = keywords[:5]  # 상위 5개 키워드만 사용
            logger.debug(f"쿼리에서 자동 추출한 키워드: {keywords}")
        
        # API 호출 관련 코드 제거
        
        # 전문가 응답 함수 선택 (expert_responses에서 직접 expert_type.value를 사용하여 가져옵니다.)
        response_func = expert_responses.get(expert_type)
        
        if response_func is None:
            logger.error(f"존재하지 않거나 MVP 범위에 없는 전문가 유형: {expert_type}")
            # MVP 범위에 없는 전문가 유형에 대한 응답 처리
            return "죄송합니다. 현재 이 분야의 전문가 서비스는 제공되지 않습니다.", [], None
        
        # 전문가 응답 함수 호출
        logger.debug(f"'{expert_type}' ({expert_class_name}) 전문가 응답 함수 호출: 키워드={keywords}")
        
        # TODO: 전문가 응답 함수의 반환 값이 (text, cards) 형태인지 (text, cards, action) 형태인지 확인 및 처리 필요
        # 현재는 (text, cards)를 기본으로 가정하고 action은 None으로 처리
        # policy_response 함수는 (text, cards)를 반환합니다.
        # 향후 다른 전문가가 action을 반환하는 경우 여기에 로직 추가 필요
        result = await response_func(query, keywords, conversation_history)

        if isinstance(result, tuple) and len(result) >= 2:
             answer = result[0]
             cards = result[1]
             action = result[2] if len(result) > 2 else None # result 튜플의 세 번째 요소가 action이라고 가정
        else:
             # 예상치 못한 결과 형식 로깅 및 처리
             logger.error(f"전문가 응답 함수의 반환 형식이 예상과 다릅니다: {type(result)}")
             answer = "죄송합니다. 응답 처리 중 오류가 발생했습니다."
             cards = []
             action = None

        logger.info(f"전문가 응답 생성 완료: {expert_class_name} - {len(cards)}개의 카드 생성됨, 응답길이={len(answer)}")
        return answer, cards, action
        
    except Exception as e:
        logger.error(f"전문가 응답 생성 중 오류 발생: {e}", exc_info=True)
        return "죄송합니다. 응답을 생성하는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.", [], None

def get_available_experts() -> List[Dict[str, Any]]:
    """
    사용 가능한 모든 전문가 정보를 반환합니다.
    
    Returns:
        전문가 정보 목록
    """
    from app.service.experts.policy_expert import PolicyExpert
    
    
    experts = [
        PolicyExpert(),

    ]
    
    return [
        {
            "id": expert.expert_type.value,
            "name": expert_type_names[expert.expert_type], # 수정된 expert_type_names 사용
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
    # 수정된 expert_names_to_type 사용
    return expert_names_to_type.get(name)

# ExpertType enum을 한글 이름으로 매핑하는 함수 (필요 시 사용)
def get_expert_name(expert_type: ExpertType) -> str:
    """
    ExpertType enum 값으로 한글 이름을 찾습니다.
    """
    # 수정된 expert_type_names 사용
    return expert_type_names.get(expert_type, expert_type.value) 