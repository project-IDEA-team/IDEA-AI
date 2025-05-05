# IDEA-AI: 장애인 복지 정보 AI 챗봇 시스템

이 프로젝트는 장애인 복지 정보를 제공하는 AI 챗봇 시스템입니다. 사용자의 질문에 맞는 정책, 취업, 복지, 창업, 의료, 교육, 상담 정보를 제공합니다.

## 시스템 구조

IDEA-AI 챗봇 시스템은 다음과 같은 구조로 설계되었습니다:

### 전체 시스템 아키텍처

```
flowchart TD
    User[사용자] <--> ChatbotUI[챗봇 UI\n- React\n- TSX\n- Tailwind CSS]
    
    subgraph "Frontend"
        ChatbotUI
    end
    
    subgraph "Backend System"
        ChatbotUI <--> GeneralAI[일반 챗봇 AI\n- 일상 대화 처리\n- 사용자 요청 수집]
        GeneralAI -- "대화 요약 전달" --> SupervisorAI[슈퍼바이저 AI Agent\n- 요약 분석\n- 키워드 추출\n- 적합한 전문가 AI 선택]
        
        SupervisorAI -- "관련 키워드 전달" --> ExpertAIs
        
        subgraph "ExpertAIs[전문가 AI 시스템]"
            Expert1[취업정보 전문가 AI]
            Expert2[창업정보 전문가 AI]
            Expert3[교육/훈련 전문가 AI]
            Expert4[정책 전문가 AI]
            Expert5[의료/건강 전문가 AI]
            Expert6[복지정보 전문가 AI]
            Expert7[심리/고충 상담 전문가 AI]
        end
        
        ExpertAIs -- "전문 정보 반환" --> SupervisorAI
        SupervisorAI -- "종합된 정보 전달" --> GeneralAI
        GeneralAI -- "사용자 친화적 응답" --> ChatbotUI
    end
    
    subgraph "Data Sources"
        ExpertAIs <--> PublicData[(공공데이터포털\nAPIs)]
        ExpertAIs <--> Database[(내부 데이터베이스)]
    end
```

### 시퀀스 다이어그램

```
sequenceDiagram
    autonumber
    participant User as 사용자
    participant UI as 챗봇 UI
    participant General as 일반 챗봇 AI
    participant Supervisor as 슈퍼바이저 AI
    participant Expert as 전문가 AI 시스템
    participant API as 공공데이터 API

    User->>UI: 질문/요청 입력
    UI->>General: 사용자 메시지 전달
    General->>General: 대화 내용 분석 및 요약
    General->>Supervisor: 대화 요약 전달
    Supervisor->>Supervisor: 키워드 추출 및 의도 분류
    Supervisor->>Expert: 작업 할당 및 키워드 전달
    Expert->>API: 공공데이터 요청
    API->>Expert: 관련 데이터 반환
    Expert->>Expert: 데이터 가공 및 분석
    Expert->>Supervisor: 전문 정보 반환
    Supervisor->>Supervisor: 다중 전문가 응답 종합
    Supervisor->>General: 종합된 정보 전달
    General->>General: 사용자 친화적 응답 생성
    General->>UI: 최종 응답 전달
    UI->>User: 답변 출력
```

### 시스템 컴포넌트

```
flowchart TB
    subgraph Frontend["프론트엔드 (React, TSX, Tailwind CSS)"]
        UI[챗봇 UI 컴포넌트]
        MessageDisplay[메시지 디스플레이]
        InputForm[입력 폼]
        AccessFeatures[접근성 기능]
    end
    
    subgraph AIBackend["AI 백엔드 (FastAPI)"]
        FastAPI[FastAPI App]
        
        subgraph AgentSystem["AI 에이전트 시스템"]
            GeneralChatbot[일반 챗봇 AI]
            SupervisorAgent[슈퍼바이저 AI]
            
            subgraph ExpertSystem["전문가 AI 시스템"]
                JobExpert[취업정보 전문가]
                StartupExpert[창업정보 전문가]
                EduExpert[교육/훈련 전문가]
                PolicyExpert[정책 전문가]
                HealthExpert[의료/건강 전문가]
                WelfareExpert[복지정보 전문가]
                CounselingExpert[심리/고충 상담 전문가]
            end
        end
        
        subgraph Utils["유틸리티"]
            NLP[자연어 처리]
            DataProcessor[데이터 가공]
            Caching[캐싱 시스템]
        end
        
        subgraph APIServices["API 서비스"]
            PublicDataClient[공공데이터 클라이언트]
        end
    end
    
    subgraph DataSources["데이터 소스"]
        PublicDataPortal[공공데이터포털 API]
        Database[(내부 데이터베이스)]
    end
```

## 기술 스택

- **Backend**: FastAPI, Python, OpenAI API
- **Frontend**: React, TypeScript, Tailwind CSS
- **AI 모델**: GPT-4o
- **데이터베이스**: MongoDB

## 디렉토리 구조

```
IDEA-AI/
├── app/
│   ├── data/            # 데이터 리소스
│   ├── models/          # 데이터 모델 정의
│   ├── router/          # API 라우터
│   ├── service/         # 서비스 로직
│   │   ├── agents/      # AI 에이전트 시스템
│   │   ├── experts/     # 전문가 AI 모듈
│   │   ├── tools/       # 도구 및 기능 모듈
│   │   └── utils/       # 유틸리티 함수
│   ├── scripts/         # 스크립트 및 도구
│   └── main.py          # 애플리케이션 진입점
├── tests/               # 테스트 코드
├── .env                 # 환경 변수
├── .gitignore
├── requirements.txt     # 의존성 패키지
└── README.md            # 프로젝트 설명
```

## API 엔드포인트

- `POST /api/chatbot/start`: 챗봇 세션 시작
- `POST /api/chatbot/expert`: 특정 전문가 AI에게 질문 전달
- `POST /api/chatbot/conversation`: 대화 흐름 처리 (일반 챗봇 -> 슈퍼바이저 -> 전문가 AI -> 응답)

## 설치 및 실행

1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

2. 환경 변수 설정
   ```
   OPENAI_API_KEY=your_api_key
   MONGODB_URI=your_mongodb_uri
   ```

3. 서버 실행
   ```bash
   uvicorn app.main:app --reload
   ```

## 전문가 AI 유형

1. **정책 전문가**: 장애인 관련 법률, 제도, 정책 등에 대한 정보 제공
2. **취업 전문가**: 장애인 취업 정보, 구직 활동 지원, 직업 훈련 등 정보 제공
3. **복지 전문가**: 장애인 복지 서비스, 혜택 등에 대한 정보 제공
4. **창업 전문가**: 장애인 창업 지원, 창업 교육, 자금 지원 등 정보 제공
5. **의료 전문가**: 장애인 의료 지원, 재활 치료, 건강 관리 등 정보 제공
6. **교육 전문가**: 장애인 교육 프로그램, 학습 지원, 특수 교육 등 정보 제공
7. **상담 전문가**: 장애인과 가족의 심리, 정서적 고충에 대한 상담 제공 