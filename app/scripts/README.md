# 크롤링 및 데이터 처리 스크립트

이 디렉토리에는 장애인 복지 정보를 수집하고 처리하기 위한 스크립트들이 포함되어 있습니다.
현재는 챗봇 백엔드의 일부로 유지되고 있으나, 장기적으로는 별도의 마이크로서비스로 분리될 예정입니다.

## 파일 구조

- `crawl_kead.py`: 한국장애인고용공단(KEAD) 웹사이트에서 정보를 크롤링하는 스크립트
- `upload_to_mongo.py`: 크롤링한 데이터를 MongoDB에 업로드하는 스크립트
- `policies.json`: 크롤링된 정책 데이터 저장 파일 (crawl_kead.py에 의해 생성됨)

## 관련 코드

다음 파일들은 크롤링된 데이터를 처리하는 데 관련이 있습니다:

- `app/service/embedding.py`: OpenAI API를 사용하여 텍스트 임베딩을 생성
- `app/service/mongodb.py`: MongoDB 연결 및 검색 유틸리티

## 사용 방법

### 1. 크롤링 실행

```bash
cd app/scripts
python crawl_kead.py
```

이 스크립트는 다양한 장애인 복지 웹페이지를 크롤링하여 `policies.json` 파일을 생성합니다.

### 2. MongoDB 업로드

```bash
cd app/scripts
python upload_to_mongo.py
```

이 스크립트는 생성된 `policies.json` 파일의 내용을 파싱하여 MongoDB에 업로드합니다.

### 3. 임베딩 생성

```bash
cd app
python -m service.embedding
```

이 스크립트는 MongoDB의 문서에 대한 텍스트 임베딩을 생성하여 데이터베이스에 저장합니다.

## 주의사항

- 이 스크립트들은 프로덕션 환경에서 정기적으로 실행되어야 합니다.
- 크롤링 시 해당 웹사이트의 이용 정책을 준수해야 합니다.
- 과도한 크롤링은 대상 서버에 부담을 줄 수 있으므로 적절한 간격을 두고 실행하세요.
- MongoDB 연결 정보와 OpenAI API 키는 환경 변수를 통해 안전하게 관리해야 합니다.

## 향후 계획

장기적으로는 이 크롤링 코드를 별도의 마이크로서비스로 분리하여 다음과 같은 기능을 구현할 예정입니다:

1. 스케줄러를 통한 자동 크롤링
2. 데이터 변경 감지 및 알림
3. 크롤링 작업 모니터링 및 로깅
4. 오류 복구 메커니즘

자세한 내용은 `app/CRAWLING_ARCHITECTURE.md` 문서를 참조하세요. 