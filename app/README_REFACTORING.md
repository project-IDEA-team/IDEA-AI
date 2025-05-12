# 챗봇 전용 백엔드 코드 리팩토링 가이드

## 개요

이 프로젝트는 원래 FastAPI 기반의 AI 챗봇과 공공데이터 API 호출 기능을 모두 포함하고 있었으나, 공공데이터 API 호출 관련 코드를 Java Spring Boot 백엔드로 이전하기 위해 리팩토링되었습니다. 이 문서는 리팩토링 과정과 결과물을 설명합니다.

## 리팩토링 목표

1. FastAPI 백엔드를 '챗봇 전용' 백엔드로 유지
2. 모든 공공데이터 API 호출 관련 코드 제거 또는 비활성화
3. Java Spring Boot 백엔드로 이전할 코드 명확히 식별
4. 크롤링 코드를 별도 마이크로서비스로 분리 준비

## 주요 변경사항

### 1. 메인 애플리케이션 (main.py)
- 애플리케이션 제목 및 설명 변경: "장애인 복지 AI 챗봇 전용 API"로 명시
- 설명에 "API 호출 로직 없음" 추가

### 2. 라우터 (router/chatbot.py)
- API 호출 관련 엔드포인트 제거
- 관련 import 문 정리 (LLMAgent 등)

### 3. 전문가 클래스 (service/experts/*)
- ApiManager 의존성 제거
- API 호출 메서드 대체 (고정된 기본 데이터 반환 방식으로 변경)
- API 호출 없이 OpenAI만으로 응답 생성하도록 수정
- 불필요한 코드와 처리 로직 제거
- 대화 이력 처리를 위한 _prepare_messages 메서드 추가
- 응답 형식 통일 (text, cards 키 사용)

### 4. 크롤링 관련 코드 (scripts/*)
- 크롤링 스크립트를 scripts/ 디렉토리로 이동
- MongoDB 연동 코드 분리
- 향후 별도 마이크로서비스로 분리 예정

### 5. MongoDB 연동 코드 (service/mongodb.py)
- 더 이상 사용하지 않음을 나타내는 주석 추가
- 실제 데이터베이스 연결 비활성화

### 6. 공공데이터 API 관련 파일
- `service/public_api/` 디렉토리 전체를 Java Spring Boot로 이전 예정
- `service/public_api/MIGRATION.md` 파일 추가 - 마이그레이션 가이드
- `app/MIGRATION_PLAN.md` 파일 추가 - 전체 마이그레이션 계획

## 새로운 아키텍처

```
[사용자] <--> [React 프론트엔드] <--> [FastAPI 백엔드] <--> [OpenAI API]
                    ^
                    |
                    v
            [Java Spring Boot 백엔드] <--> [공공데이터 API들]
                    ^
                    |
                    v
            [Python 크롤링 마이크로서비스] <--> [MongoDB]
```

- **FastAPI 백엔드**: OpenAI와 연동하여 AI 챗봇 기능만 담당
- **Java Spring Boot 백엔드**: 공공데이터 API 호출 및 데이터 처리 담당
- **Python 크롤링 마이크로서비스**: 데이터 수집 및 MongoDB 저장 담당

## 완료된 작업

1. 모든 전문가 클래스 리팩토링 완료
   - API 호출 코드 제거 및 고정 데이터 반환으로 대체
   - 응답 생성 로직 단순화 (OpenAI API만 사용)
   - 대화 이력 처리 방식 일관성 유지
   - 응답 형식 통일 (text, cards 키 사용)

2. 기본 정보 카드 제공 로직 구현
   - 각 전문 분야에 맞는 기본 정보 카드 준비
   - API 호출 없이도 유용한 정보 제공

3. 크롤링 코드 구조화
   - scripts/ 디렉토리로 이동
   - 독립적인 실행 환경 구성
   - MongoDB 연동 코드 분리

## 추가 작업 필요사항

1. 테스트 및 검증
   - 모든 챗봇 기능이 API 호출 없이도 정상 작동하는지 확인
   - 응답 품질 유지 여부 검증

2. Java Spring Boot 백엔드 구현
   - 상세 구현 방법은 `app/service/public_api/MIGRATION.md` 참조

3. 크롤링 마이크로서비스 분리
   - 상세 계획은 `app/CRAWLING_ARCHITECTURE.md` 참조 