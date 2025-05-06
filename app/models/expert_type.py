from enum import Enum

class ExpertType(str, Enum):
    POLICY = "정책"
    EMPLOYMENT = "취업"
    WELFARE = "복지"
    STARTUP = "창업"
    MEDICAL = "의료"
    EDUCATION = "교육"
    COUNSELING = "상담" 