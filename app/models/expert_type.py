from enum import Enum

class ExpertType(str, Enum):
    POLICY = "정책"
    EMPLOYMENT = "취업"
    WELFARE = "복지"
    STARTUP = "창업"
    MEDICAL = "의료"
    EDUCATION = "교육"
    COUNSELING = "상담"
    # 기업회원용 전문가 타입
    EMPLOYMENT_POLICY = "고용 정책"
    JOB_SEEKERS = "구직자 현황"
    CONSULTING = "고용 컨설팅"
    APPLICATION_MANAGE = "지원의향서" 