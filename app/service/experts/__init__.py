from typing import Dict, List, Any, Optional
import logging
from app.models.expert_type import ExpertType, UserType

from .expert import Expert

logger = logging.getLogger(__name__)

# 전문가 유형별 이름 매핑
expert_names = {
    # 장애인용 전문가
    ExpertType.POLICY: "정책 전문가",
    ExpertType.EMPLOYMENT: "취업/창업 전문가",
    
    # 기업용 전문가
    ExpertType.COMPANY_POLICY: "기업 정책 전문가",
    ExpertType.RECRUITMENT: "구인/인재 전문가"
}

# 이름으로 전문가 유형 찾기
expert_name_to_type = {v: k for k, v in expert_names.items()}

class ExpertFactory:
    """전문가 AI 인스턴스를 생성하고 관리하는 팩토리 클래스"""
    
    _experts: Dict[ExpertType, Expert] = {}
    
    @classmethod
    def get_expert(cls, expert_type: ExpertType) -> Optional[Expert]:
        """
        전문가 유형에 따른 전문가 AI 인스턴스를 반환합니다.
        
        Args:
            expert_type: 전문가 유형
            
        Returns:
            Expert 인스턴스 또는 None
        """
        try:
            if expert_type not in cls._experts:
                cls._experts[expert_type] = Expert(expert_type)
            return cls._experts[expert_type]
        except Exception as e:
            logger.error(f"전문가 인스턴스 생성 중 오류 발생: {str(e)}")
            return None
    
    @classmethod
    def get_experts_for_user(cls, user_type: UserType) -> Dict[ExpertType, Expert]:
        """
        사용자 유형에 따른 전문가 목록을 반환합니다.
        
        Args:
            user_type: 사용자 유형
            
        Returns:
            전문가 유형별 Expert 인스턴스 딕셔너리
        """
        experts = {}
        for expert_type in ExpertType.get_experts_for_user(user_type):
            expert = cls.get_expert(expert_type)
            if expert:
                experts[expert_type] = expert
        return experts
    
    @classmethod
    def get_expert_by_name(cls, name: str) -> Optional[Expert]:
        """
        전문가 이름으로 Expert 인스턴스를 반환합니다.
        
        Args:
            name: 전문가 이름
            
        Returns:
            Expert 인스턴스 또는 None
        """
        expert_type = expert_name_to_type.get(name)
        if expert_type:
            return cls.get_expert(expert_type)
        return None
    
    @classmethod
    def get_expert_name(cls, expert_type: ExpertType) -> str:
        """
        전문가 유형에 해당하는 이름을 반환합니다.
        
        Args:
            expert_type: 전문가 유형
            
        Returns:
            전문가 이름
        """
        return expert_names.get(expert_type, "알 수 없는 전문가") 