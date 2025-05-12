# 모든 전문가들은 반드시 아래와 같은 JSON 형식으로 정보 카드를 생성해야 합니다.
#
# {
#   "id": "string",
#   "title": "string",
#   "subtitle": "string",
#   "summary": "string",
#   "type": "string",
#   "details": "string",
#   "source": {
#     "url": "string",
#     "name": "string",
#     "phone": "string"
#   },
#   "buttons": [
#     {"type": "link", "label": "string", "value": "string"},
#     {"type": "tel", "label": "string", "value": "string"}
#   ]
# }

# 아래는 각 전문가별 예시 카드 템플릿입니다.

# 공통 카드 템플릿 모음 (education_cards 포맷 기준)

EDUCATION_CARD_TEMPLATE = {
    "id": "education-info-general",
    "title": "장애인 교육 지원 정보",
    "subtitle": "교육 지원",
    "summary": "장애인을 위한 주요 교육 지원 제도 안내",
    "type": "education",
    "details": "장애인을 위한 주요 교육 지원 제도 및 서비스 안내입니다.",
    "source": {
        "url": "https://www.nise.go.kr",
        "name": "국립특수교육원",
        "phone": "041-537-1500"
    },
    "buttons": [
        {"type": "link", "label": "자세히 보기", "value": "https://www.nise.go.kr"},
        {"type": "tel", "label": "국립특수교육원", "value": "041-537-1500"}
    ]
}

EMPLOYMENT_CARD_TEMPLATE = {
    "id": "employment-info",
    "title": "장애인 취업/창업 지원",
    "subtitle": "한국장애인고용공단",
    "summary": "맞춤형 취업 정보와 창업 지원 서비스 안내",
    "type": "employment",
    "details": "취업/창업 지원 서비스:\n- 맞춤형 일자리 정보\n- 직업능력개발 훈련\n- 창업 교육 및 컨설팅\n- 취업 성공 사례",
    "source": {
        "url": "https://www.kead.or.kr",
        "name": "한국장애인고용공단",
        "phone": "1588-1519"
    },
    "buttons": [
        {
            "type": "link",
            "label": "취업 정보",
            "value": "https://www.kead.or.kr"
        },
        {
            "type": "tel",
            "label": "상담 문의",
            "value": "1588-1519"
        }
    ]
}

WELFARE_CARD_TEMPLATE = {
    "id": "welfare-general",
    "title": "장애인 복지 서비스 안내",
    "subtitle": "복지 정보",
    "summary": "장애인을 위한 다양한 복지 서비스 종합 안내",
    "type": "welfare",
    "details": "장애인을 위한 주요 복지 서비스 안내입니다.",
    "source": {
        "url": "https://www.bokjiro.go.kr",
        "name": "복지로",
        "phone": "129"
    },
    "buttons": [
        {"type": "link", "label": "복지로 홈페이지", "value": "https://www.bokjiro.go.kr"},
        {"type": "tel", "label": "보건복지상담센터", "value": "129"}
    ]
}

POLICY_CARD_TEMPLATE = {
    "id": "policy-info",
    "title": "장애인 종합 지원 정책",
    "subtitle": "보건복지부",
    "summary": "장애인을 위한 의료, 복지, 취업 관련 정부 지원 정책",
    "type": "policy",
    "details": "장애인을 위한 주요 지원 정책 안내:\n- 의료비 지원\n- 보조기기 지원\n- 활동지원 서비스\n- 취업 지원 프로그램",
    "source": {
        "url": "https://www.bokjiro.go.kr",
        "name": "복지로",
        "phone": "129"
    },
    "buttons": [
        {
            "type": "link",
            "label": "자세히 보기",
            "value": "https://www.bokjiro.go.kr"
        },
        {
            "type": "tel",
            "label": "상담 문의",
            "value": "129"
        }
    ]
}

MEDICAL_CARD_TEMPLATE = {
    "id": "medical-info-1",
    "title": "장애인 건강 및 의료 지원 안내",
    "subtitle": "의료 지원",
    "summary": "장애인을 위한 건강관리 및 의료지원 서비스 종합 안내",
    "type": "medical",
    "details": "장애인을 위한 주요 의료 지원 서비스 안내입니다.",
    "source": {
        "url": "https://www.mohw.go.kr",
        "name": "보건복지부",
        "phone": "129"
    },
    "buttons": [
        {"type": "link", "label": "자세히 보기", "value": "https://www.mohw.go.kr"},
        {"type": "tel", "label": "보건복지상담센터", "value": "129"}
    ]
}

STARTUP_CARD_TEMPLATE = {
    "id": "startup-general",
    "title": "장애인 창업 종합 정보",
    "subtitle": "창업 안내",
    "summary": "장애인 창업에 필요한 기본 정보와 지원 제도 안내",
    "type": "startup",
    "details": "장애인 창업을 위한 기본 정보와 지원 제도입니다.",
    "source": {
        "url": "https://www.debc.or.kr",
        "name": "장애인기업종합지원센터",
        "phone": "02-2181-6500"
    },
    "buttons": [
        {"type": "link", "label": "창업 지원 안내", "value": "https://www.debc.or.kr"},
        {"type": "tel", "label": "상담 문의", "value": "02-2181-6500"}
    ]
}

COUNSELING_CARD_TEMPLATE = {
    "id": "counseling-info-1",
    "title": "장애인 심리상담 서비스",
    "subtitle": "심리상담",
    "summary": "장애인과 가족을 위한 심리상담 지원 서비스",
    "type": "counseling",
    "details": "장애인 심리상담 서비스 안내입니다.",
    "source": {
        "url": "https://www.kawid.or.kr",
        "name": "한국장애인재활협회",
        "phone": "02-3472-3556"
    },
    "buttons": [
        {"type": "link", "label": "자세히 보기", "value": "https://www.kawid.or.kr"},
        {"type": "tel", "label": "전화 문의", "value": "02-3472-3556"}
    ]
}

# 기업용 전문가 카드 템플릿

COMPANY_POLICY_CARD_TEMPLATE = {
    "id": "company-policy-info",
    "title": "장애인 고용 지원 제도",
    "subtitle": "고용노동부",
    "summary": "기업의 장애인 고용을 위한 법률 및 지원 제도 안내",
    "type": "company_policy",
    "details": "주요 지원 제도:\n- 장애인 고용 장려금\n- 시설장비 지원금\n- 고용관리 비용 지원\n- 표준사업장 설립 지원",
    "source": {
        "url": "https://www.moel.go.kr",
        "name": "고용노동부",
        "phone": "1350"
    },
    "buttons": [
        {
            "type": "link",
            "label": "자세히 보기",
            "value": "https://www.moel.go.kr"
        },
        {
            "type": "tel",
            "label": "고용공단 문의",
            "value": "1350"
        }
    ]
}

RECRUITMENT_CARD_TEMPLATE = {
    "id": "recruitment-info",
    "title": "장애인 인재 채용 안내",
    "subtitle": "한국장애인고용공단",
    "summary": "기업 맞춤형 장애인 인재 추천 서비스",
    "type": "recruitment",
    "details": "채용 지원 서비스:\n- 맞춤형 인재 추천\n- 구직자 프로필 검색\n- 채용 절차 컨설팅\n- 정부 지원금 안내",
    "source": {
        "url": "https://www.kead.or.kr",
        "name": "한국장애인고용공단",
        "phone": "1588-1519"
    },
    "buttons": [
        {
            "type": "link",
            "label": "인재 검색",
            "value": "https://www.kead.or.kr"
        },
        {
            "type": "tel",
            "label": "채용 문의",
            "value": "1588-1519"
        }
    ]
} 