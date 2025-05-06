from .counseling_expert import counseling_response
from .policy_expert import policy_response
from app.models.expert_type import ExpertType
from typing import List, Dict, Any, Tuple, Optional
import uuid

async def get_expert_response(query: str, expert_type: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> tuple:
    """
    전문가 유형에 따라 적절한 응답을 생성합니다.
    
    Args:
        query: 사용자 질문
        expert_type: 전문가 유형
        conversation_history: 이전 대화 내용
        
    Returns:
        응답 텍스트와 카드 목록
    """
    if expert_type == "전문 상담" or expert_type == ExpertType.COUNSELING.value:
        answer, cards = await counseling_response(query, conversation_history)
    elif expert_type == "정책" or expert_type == ExpertType.POLICY.value:
        answer, cards = await policy_response(query, None, conversation_history)
    # TODO: 다른 전문가 모듈 연결
    # elif expert_type == "취업" or expert_type == ExpertType.EMPLOYMENT.value:
    #     return await employment_response(query)
    # elif expert_type == "복지" or expert_type == ExpertType.WELFARE.value:
    #     return await welfare_response(query)
    # elif expert_type == "창업" or expert_type == ExpertType.STARTUP.value:
    #     return await startup_response(query)
    # elif expert_type == "의료" or expert_type == ExpertType.MEDICAL.value:
    #     return await medical_response(query)
    # elif expert_type == "교육" or expert_type == ExpertType.EDUCATION.value:
    #     return await education_response(query)
    else:
        answer, cards = f"{expert_type} 전문가 응답입니다. 추가 정보를 제공할 수 없습니다.", []

    # 카드 데이터가 None이거나 리스트/딕셔너리 형태가 아니면 fallback 처리
    if not cards:
        cards = []
    elif not isinstance(cards, list):
        cards = [cards]
    # 각 카드가 딕셔너리인지 확인, 아니면 텍스트를 details로 하는 기본 카드로 변환
    safe_cards = []
    for card in cards:
        if isinstance(card, dict):
            safe_cards.append(card)
        else:
            safe_cards.append({
                "id": str(uuid.uuid4()),
                "title": "관련 정보",
                "type": "policy",
                "summary": "챗봇이 제공하는 관련 정보입니다.",
                "details": str(card)
            })
    return answer, safe_cards 