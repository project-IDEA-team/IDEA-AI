# IDEA-AI (Python AI Backend)

> **장애인 고용 지원 정책을 AI로 요약·상담해주는 백엔드 서비스**  
> 공공데이터와 AI 모델을 결합해, 복잡한 정책을 더 쉽게 이해할 수 있도록 돕습니다.

📆 개발 기간: 2024.03 ~ 2024.05  
👥 팀원: 임현성, 진소영, 황주영, 함민규

---

## 💡 프로젝트 개요

이 리포지토리는 **AI 기반 요약 및 챗봇 기능**을 제공하는 Python 백엔드입니다.  
장애인 구직자와 고용주를 위한 정부 정책 정보를 자연어로 요약·상담해주는 역할을 담당합니다.

- **프론트엔드(React)**, **일반 백엔드(Spring Boot)**와 연동하여 동작합니다.
- OpenAI API, MongoDB 등 다양한 외부 서비스와 연동됩니다.

---

## 주요 기능

* ✅ **AI 챗봇**: 사용자의 질문에 대해 정책 정보를 요약하여 답변
* ✅ **정책 임베딩 검색**: MongoDB에 저장된 정책 문서에서 유사한 정책 검색
* ✅ **OpenAI 연동**: GPT-4o-mini 등 최신 LLM을 활용한 자연어 처리
* ✅ **카드형 정책 정보 제공**: 프론트엔드에서 활용할 수 있는 카드 데이터 반환

---

## 📦 폴더 구조

```
IDEA-AI/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI 진입점
│   ├── router/
│   │   ├── __init__.py
│   │   └── chatbot.py         # 챗봇 관련 FastAPI 라우터
│   ├── service/
│   │   ├── __init__.py
│   │   ├── embedding.py       # OpenAI 임베딩 생성
│   │   ├── embedding_bge-m3.py# BGE-M3 임베딩 생성
│   │   └── mongodb.py         # MongoDB 연동 및 검색
│   └── scripts/
│       ├── crawl_kead.py      # 정책 데이터 크롤러
│       ├── policies.json      # 크롤링된 정책 데이터 샘플
│       └── upload_to_mongo.py # 정책 데이터 MongoDB 업로드
├── requirements.txt           # Python 의존성 목록
├── README.md                  # 프로젝트 설명 파일
└── .gitignore
```

---

## ⚙️ 주요 기술 스택

- **Python 3.10+**
- **FastAPI**: 비동기 REST API 서버
- **OpenAI API**: GPT-4o-mini 등 LLM 활용
- **MongoDB**: 정책 데이터 저장 및 검색
- **Pydantic**: 데이터 모델링 및 검증

---

## 🚀 실행 방법

1. 의존성 설치
    ```bash
    pip install -r requirements.txt
    ```

2. 환경 변수(.env) 설정  
   (OpenAI API 키, MongoDB 접속 정보 등)

3. 서버 실행
    ```bash
    uvicorn app.main:app --reload
    ```

---

## 🗂️ 주요 파일 설명

- `app/router/chatbot.py`  
  챗봇 질의 응답 및 정책 카드 반환 API

- `app/service/embedding.py`  
  OpenAI 임베딩 생성 및 벡터 검색

- `app/service/mongodb.py`  
  MongoDB에서 정책 데이터 검색

- `document/`  
  정책 원문 데이터 및 샘플

- `requirements.txt`  
  Python 패키지 의존성 목록

---

## ✨ 기여 및 문의

- Pull Request, Issue 환영합니다!
- 문의: 팀원 또는 GitHub Issue 활용

---

## 참고

- [IDEA-frontend (React)](https://github.com/project-IDEA-team/IDEA-frontend)
- [IDEA-backend (Spring Boot)](https://github.com/project-IDEA-team/IDEA-backend)

--- 