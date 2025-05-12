from enum import Enum

class UserType(str, Enum):
    """사용자 유형"""
    DISABLED = "disabled"  # 장애인
    COMPANY = "company"    # 기업

class ExpertType(str, Enum):
    """전문가 유형"""
    # 장애인용 전문가
    POLICY = "policy"      # 정책 전문가 (의료, 복지, 취업 정책)
    EMPLOYMENT = "employment"  # 취업/창업 전문가
    
    # 기업용 전문가
    COMPANY_POLICY = "company_policy"  # 기업 정책 전문가
    RECRUITMENT = "recruitment"        # 구인/인재추천 전문가

    @classmethod
    def get_experts_for_user(cls, user_type: UserType) -> list:
        """사용자 유형에 따른 전문가 목록 반환"""
        if user_type == UserType.DISABLED:
            return [cls.POLICY, cls.EMPLOYMENT]
        elif user_type == UserType.COMPANY:
            return [cls.COMPANY_POLICY, cls.RECRUITMENT]
        return []

    # 기업회원용 전문가 타입
    EMPLOYMENT_POLICY = "고용 정책"
    JOB_SEEKERS = "구직자 현황"
    CONSULTING = "고용 컨설팅"
    APPLICATION_MANAGE = "지원의향서" 