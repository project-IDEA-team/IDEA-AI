# IDEA-AI: 장애인 고용 지원 AI 시스템

## 📌 프로젝트 개요
IDEA-AI는 장애인 고용 지원을 위한 AI 기반 시스템입니다. 이 시스템은 장애인 고용 관련 정책, 제도, 지원금 등의 정보를 제공하고, 사용자의 질문에 대해 정확하고 유용한 답변을 제공합니다.

## 🚀 주요 기능
- 장애인 고용 관련 정책 및 제도 정보 제공
- 지원금 및 혜택 안내
- FAQ 및 상담 지원
- 맞춤형 정보 추천

## 🛠️ 기술 스택
- Python 3.8+
- FastAPI
- LangChain
- OpenAI GPT
- MongoDB
- BeautifulSoup4

## 📁 프로젝트 구조
```
IDEA-AI/
├── app/
│   ├── data/                    # 데이터 파일 저장
│   │   └── counseling/         # 상담 관련 데이터
│   ├── models/                 # 데이터 모델 정의
│   │   ├── policy_card.py     # 정책 카드 모델
│   │   └── expert_type.py     # 전문가 유형 정의
│   ├── router/                # API 라우터
│   │   └── chatbot.py        # 챗봇 API 엔드포인트
│   ├── scripts/              # 유틸리티 스크립트
│   │   ├── crawl_kead.py    # 웹 크롤링 스크립트
│   │   └── upload_to_mongo.py # DB 업로드 스크립트
│   ├── service/             # 핵심 서비스 로직
│   │   ├── agents/         # AI 에이전트
│   │   │   ├── general_chatbot.py
│   │   │   └── supervisor.py
│   │   ├── experts/       # 전문가 AI
│   │   │   ├── base_expert.py
│   │   │   ├── counseling_expert.py
│   │   │   └── policy_expert.py
│   │   ├── tools/        # 유틸리티 도구
│   │   │   └── counseling_tools.py
│   │   ├── utils/       # 공통 유틸리티
│   │   │   ├── cache.py
│   │   │   └── data_processor.py
│   │   ├── embedding.py    # 임베딩 처리
│   │   ├── mongodb.py     # DB 연동
│   │   └── openai_client.py # OpenAI 클라이언트
│   └── main.py           # 애플리케이션 진입점
├── document/            # 프로젝트 문서
├── tests/             # 테스트 코드
├── .env.example      # 환경 변수 예시
├── .gitignore       # Git 제외 파일
├── README.md       # 프로젝트 설명
├── requirements.txt # 의존성 목록
└── system_overview.md # 시스템 개요
```

## ⚠️ 주의사항
현재 다음 기능들은 개발 중이며 주석 처리되어 있습니다:
- `app/service/utils/data_processor.py`의 `extract_structured_data` 메서드
- `app/service/tools/counseling_tools.py`의 `search_counseling_centers` 메서드
- `app/service/experts/policy_expert.py`의 `search_policy_database` 메서드
- `app/scripts/crawl_kead.py`의 전체 크롤링 스크립트

## 🚀 시작하기
1. 저장소 클론
```bash
git clone https://github.com/your-username/IDEA-AI.git
cd IDEA-AI
```

2. 가상환경 설정
```bash
conda create -n idea-ai python=3.8
conda activate idea-ai
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 API 키와 설정을 추가
```

5. 서버 실행
```bash
uvicorn app.main:app --reload
```

## 📝 라이선스
MIT License

## 👥 기여
프로젝트에 기여하고 싶으시다면 Pull Request를 보내주세요. 