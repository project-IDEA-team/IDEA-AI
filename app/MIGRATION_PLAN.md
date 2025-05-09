# API 관련 코드 Java Spring Boot 마이그레이션 계획

## 개요
현재 FastAPI 기반 챗봇 백엔드에서 API 호출 관련 코드를 분리하여 Java Spring Boot 백엔드로 이전합니다. 이를 통해 챗봇은 AI 응답 생성에만 집중하고, 공공데이터 API 호출 및 관련 로직은 Spring Boot에서 처리합니다.

## 이전 대상

### 1. 공공데이터 API 관련 코드
- `app/service/public_api/` 디렉토리 전체
  - 각종.공공데이터 API 클라이언트 (kead, welfare, policy 등)
  - API 통합 관리자
  - 도구 정의 및 실행 코드

### 2. API 호출 관련 엔드포인트
- `/chat/api` 엔드포인트

### 3. 관련 모델 및 유틸리티
- MongoDB 연동 코드
- LLM 도구 활용 에이전트

## 구현 방법

1. **현재 Python 코드의 API 호출 로직 비활성화**
   - 관련 엔드포인트 제거
   - 공공데이터 API 관련 코드 비활성화
   - MongoDB 코드 비활성화
   
2. **Java Spring Boot 백엔드 구현**
   - RestTemplate/WebClient를 사용한 API 클라이언트 구현
   - DTO, 서비스, 컨트롤러 구현
   - MongoDB 연동 (Spring Data MongoDB)
   
3. **API 엔드포인트 매핑**
   - Python 엔드포인트를 Java 엔드포인트로 매핑
   - 새로운 API 문서 작성

4. **프론트엔드 연동 변경**
   - 챗봇 API → Python 백엔드
   - 공공데이터 API → Java 백엔드

## 크롤링 코드 아키텍처 계획

현재 웹 크롤링 관련 코드(`crawl_kead.py`, `upload_to_mongo.py`, `embedding.py`, `mongodb.py`)는 단기적으로 FastAPI 백엔드 내에 유지하되, 장기적으로는 별도의 Python 크롤링 마이크로서비스로 분리하는 것을 계획합니다.

### 1단계: 현재 아키텍처 유지 (단기)
- 크롤링 스크립트를 FastAPI 백엔드 내 `app/scripts/` 디렉토리에 유지
- MongoDB 접근 코드 유지
- 필요시 수동으로 크롤링 스크립트 실행

### 2단계: 크롤링 마이크로서비스 분리 (장기)
- 별도의 Python 프로젝트로 크롤링 코드 분리
- 스케줄러를 통한 주기적 실행 구현
- MongoDB를 공유 데이터 저장소로 활용
- 자세한 내용은 `app/CRAWLING_ARCHITECTURE.md` 참조

## 진행상황

- [x] 마이그레이션 대상 코드 식별
- [x] Python 백엔드 코드 비활성화 
- [ ] Spring Boot 백엔드 구현
- [ ] 프론트엔드 연동 변경
- [ ] 시스템 통합 테스트
- [ ] 크롤링 코드 별도 서비스로 분리 (장기 계획)

## 주의사항

1. 양쪽 백엔드 간 인증 및 권한 관리 통합이 필요할 수 있습니다.
2. 공통 데이터 형식을 정의하여 일관성 있는 API 응답을 유지해야 합니다.
3. API 키 및 비밀 정보는 환경 변수나 안전한 구성 저장소를 통해 관리해야 합니다. 
4. 크롤링 서비스 분리 시 환경 설정과 의존성 관리에 주의해야 합니다. 