from enum import Enum
from typing import Dict, List, Optional, Tuple
import re
from app.models.expert_type import ExpertType, UserType

class Intent(Enum):
    POLICY = "policy"
    EMPLOYMENT = "employment"
    COMPANY_POLICY = "company_policy"
    RECRUITMENT = "recruitment"
    UNKNOWN = "unknown"

class NLUService:
    def __init__(self):
        self.intent_patterns = {
            Intent.POLICY: [
                r"정책|법률|제도|규정|지원금|혜택|의료|복지",
                r"장애인.*지원",
                r"장애.*혜택",
                r"복지.*서비스",
                r"의료.*지원"
            ],
            Intent.EMPLOYMENT: [
                r"일자리|취업|구직|채용|면접|이력서|창업",
                r"일[을]?\s*(구하|찾|얻|하고)",
                r"취업[을]?\s*(하고|알려|가능|방법|하려|준비|도와)",
                r"창업[을]?\s*(하고|알려|방법|준비|지원)",
                r"구직[을]?\s*(하고|알려|가능|방법|하려|준비|도와)"
            ],
            Intent.COMPANY_POLICY: [
                r"기업.*의무|고용.*의무|장애인.*고용",
                r"장애인.*채용.*지원금?",
                r"시설.*개선.*지원",
                r"법적.*의무",
                r"기업.*지원금?"
            ],
            Intent.RECRUITMENT: [
                r"인재.*추천|구직자.*정보|채용.*정보",
                r"장애인.*구직자",
                r"이력서.*검색",
                r"인재.*매칭",
                r"채용.*절차"
            ]
        }
        
        self.slot_patterns = {
            "region": [
                (r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[시도]?", "region"),
                (r"([가-힣]+구)", "region"),
                (r"([가-힣]+시)", "region")
            ],
            "disability_type": [
                (r"(지체|뇌병변|시각|청각|언어|안면|신장|심장|간|호흡기|장루|요루|뇌전증|지적|자폐성|정신)\\s*장애", "disability_type")
            ],
            "job_type": [
                (r"(사무|생산|서비스|기술|영업|교육|IT|디자인|연구|개발)\\s*(직|업무|일|작업|근무)", "job_type")
            ],
            "company_size": [
                (r"(대기업|중소기업|중견기업|스타트업|공공기관|공기업)", "company_size")
            ],
            "employment_type": [
                (r"(정규직|계약직|파견직|프리랜서|아르바이트|인턴)", "employment_type")
            ]
        }

    def classify_and_extract(self, text: str, user_type: UserType) -> Tuple[Intent, Dict[str, str]]:
        """
        텍스트에서 의도를 분류하고 슬롯을 추출합니다.
        
        Args:
            text: 입력 텍스트
            user_type: 사용자 유형
            
        Returns:
            (의도, 추출된 슬롯 정보)
        """
        # 1. 의도 분류
        intent = self._classify_intent(text)
        
        # 2. 슬롯 추출
        slots = self._extract_slots(text)
        
        return intent, slots
    
    def _classify_intent(self, text: str) -> Intent:
        """텍스트에서 의도를 분류합니다."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return Intent.UNKNOWN
    
    def _extract_slots(self, text: str) -> Dict[str, str]:
        """텍스트에서 슬롯 정보를 추출합니다."""
        slots = {}
        
        for slot_type, patterns in self.slot_patterns.items():
            for pattern, slot_name in patterns:
                match = re.search(pattern, text)
                if match:
                    slots[slot_name] = match.group(1)
                    break
        
        return slots
    
    def _map_intent_to_expert(self, intent: Intent, user_type: UserType) -> ExpertType:
        """의도와 사용자 유형에 따라 전문가 유형을 결정합니다."""
        if user_type == UserType.DISABLED:
            if intent in [Intent.POLICY, Intent.UNKNOWN]:
                return ExpertType.POLICY
            return ExpertType.EMPLOYMENT
            
        elif user_type == UserType.COMPANY:
            if intent in [Intent.COMPANY_POLICY, Intent.UNKNOWN]:
                return ExpertType.COMPANY_POLICY
            return ExpertType.RECRUITMENT
        
        return ExpertType.POLICY  # 기본값 