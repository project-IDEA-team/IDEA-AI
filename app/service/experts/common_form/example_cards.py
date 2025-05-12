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
    "id": "employment-info-1",
    "title": "장애인 취업 정보",
    "subtitle": "취업 지원",
    "summary": "장애인 취업을 위한 주요 정보와 지원 제도",
    "type": "employment",
    "details": "장애인 취업을 위한 다양한 지원 제도 안내입니다.",
    "source": {
        "url": "https://www.kead.or.kr",
        "name": "한국장애인고용공단",
        "phone": "1588-1519"
    },
    "buttons": [
        {"type": "link", "label": "자세히 보기", "value": "https://www.kead.or.kr"},
        {"type": "tel", "label": "전화 문의", "value": "1588-1519"}
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
    "title": "장애인 의무고용 제도",
    "subtitle": "고용노동부",
    "summary": "기업에서 장애인을 일정 비율 이상 고용하도록 하는 제도",
    "type": "policy",
    "details": "- 내용: 일정 규모 이상 사업장에서 장애인을 일정 비율 이상 고용하도록 의무화\n- 고용률: 50인 이상 사업장 2.6% 이상(2024년 기준)\n- 문의처: 한국장애인고용공단 1350 (유료)",
    "source": {
        "url": "https://www.kead.or.kr",
        "name": "한국장애인고용공단",
        "phone": "1350"
    },
    "buttons": [
        {
            "type": "link",
            "label": "자세히 보기",
            "value": "https://www.kead.or.kr"
        },
        {
            "type": "tel",
            "label": "전화 문의",
            "value": "1350"
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