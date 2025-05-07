# IDEA-AI 공공데이터 API 연동 가이드

IDEA-AI 프로젝트에서는 기존 더미 데이터 대신 실제 공공데이터 API를 활용하여 보다 정확하고 풍부한 장애인 복지 정보를 제공합니다. 이 문서는 공공데이터 API 연동 방법과 추가 설정 사항을 설명합니다.

## 목차

1. [공공데이터 API 연동 구조](#공공데이터-api-연동-구조)
2. [환경 설정](#환경-설정)
3. [지원하는 API 목록](#지원하는-api-목록)
4. [API 클라이언트 사용법](#api-클라이언트-사용법)
5. [각 전문가별 API 연동 방법](#각-전문가별-api-연동-방법)
6. [오류 처리 및 fallback 메커니즘](#오류-처리-및-fallback-메커니즘)

## 공공데이터 API 연동 구조

IDEA-AI의 공공데이터 API 연동은 다음과 같은 구조로 설계되었습니다:

```
app/
  ├── service/
  │   ├── public_api/               # 공공데이터 API 연동 모듈
  │   │   ├── __init__.py           # 패키지 초기화
  │   │   ├── base_client.py        # 기본 API 클라이언트 클래스
  │   │   ├── api_manager.py        # API 통합 관리 클래스
  │   │   ├── policy.py             # 정책 정보 API 클라이언트
  │   │   ├── welfare.py            # 복지 정보 API 클라이언트
  │   │   ├── kead.py               # 한국장애인고용공단 API 클라이언트
  │   │   └── ...                   # 기타 API 클라이언트
  │   └── experts/                  # 전문가 모듈
  │       ├── __init__.py           # 전문가 응답 통합 함수
  │       ├── base_expert.py        # 기본 전문가 클래스
  │       ├── policy_expert.py      # 정책 전문가 클래스
  │       └── ...                   # 기타 전문가 클래스
  └── config/
      ├── __init__.py               # 패키지 초기화
      └── settings.py               # 환경 설정 관리
```

- `base_client.py`: 모든 API 클라이언트의 기본 클래스로, HTTP 요청 처리, 응답 파싱, 오류 처리 등 공통 기능 제공
- `api_manager.py`: 여러 API를 통합 관리하고 검색 키워드에 따라 적절한 API 선택
- 각 전문가 클래스: API 클라이언트를 활용하여 실제 데이터 요청 및 응답 처리

## 환경 설정

공공데이터 API를 사용하기 위해서는 다음과 같은 환경 설정이 필요합니다:

1. `.env` 파일 생성 (`.env.example` 파일을 참고하여 생성)
2. 각 공공데이터 포털에서 API 키 발급 받기
3. `.env` 파일에 API 키 설정

```env
# 공공데이터 API 키 설정
KEAD_API_KEY=your_kead_api_key             # 한국장애인고용공단
WELFARE_API_KEY=your_welfare_api_key       # 복지로
POLICY_API_KEY=your_policy_api_key         # 정부24
MOEL_API_KEY=your_moel_api_key             # 고용노동부
HRD_API_KEY=your_hrd_api_key               # 한국산업인력공단
KOSHA_API_KEY=your_kosha_api_key           # 안전보건공단
COMWEL_API_KEY=your_comwel_api_key         # 근로복지공단
KEIS_API_KEY=your_keis_api_key             # 한국고용정보원
KOSEA_API_KEY=your_kosea_api_key           # 한국사회적기업진흥원
KODDI_API_KEY=your_koddi_api_key           # 한국장애인개발원
```

API 키가 설정되지 않은 경우에도 시스템은 동작하지만, 해당 API를 사용하지 않고 백업 데이터를 활용합니다.

## 지원하는 API 목록

현재 IDEA-AI에서 지원하는 공공데이터 API 목록입니다:

| API 이름 | 제공기관 | 데이터 내용 | 변수명 |
|----------|---------|------------|-------|
| 장애인 일자리 정보 | 한국장애인고용공단 | 장애인 채용정보, 직업훈련 | KEAD_API_KEY |
| 장애인 복지서비스 | 복지로 | 복지 서비스, 급여 정보 | WELFARE_API_KEY |
| 정부 정책 정보 | 정부24 | 장애인 관련 정책 | POLICY_API_KEY |
| 취업 정보 | 한국고용정보원 | 일자리 정보, 구인정보 | KEIS_API_KEY |
| 사회적기업 정보 | 한국사회적기업진흥원 | 사회적기업 정보, 지원사업 | KOSEA_API_KEY |
| 장애인 의료지원 | 보건복지부 | 의료기관, 지원제도 | MOHW_API_KEY |
| 교육 프로그램 | 국립특수교육원 | 특수교육, 평생교육 정보 | SPECIAL_EDU_API_KEY |

## API 클라이언트 사용법

API 클라이언트는 아래와 같이 사용할 수 있습니다:

```python
from app.service.public_api.api_manager import ApiManager

# API 매니저 인스턴스 생성
api_manager = ApiManager()

# 키워드 기반 검색
results = await api_manager.search_by_keywords(["장애인", "취업"], "취업")

# 결과 활용
for item in results:
    print(f"제목: {item['title']}")
    print(f"내용: {item['details']}")
```

또는 특정 API 클라이언트를 직접 사용할 수도 있습니다:

```python
from app.service.public_api.kead import KeadApiClient

# API 클라이언트 인스턴스 생성
kead_client = KeadApiClient()

# 근로지원인 수행기관 정보 조회
agencies = await kead_client.get_support_agencies(region="서울")

# 표준사업장 정보 조회
workplaces = await kead_client.get_standard_workplaces(page=1, size=10)
```

## 각 전문가별 API 연동 방법

각 전문가 클래스에서는 다음과 같이 API를 활용합니다:

1. 전문가 클래스 초기화 시 API 매니저 인스턴스 생성
2. 사용자 쿼리에 맞는 키워드 추출
3. 키워드 기반으로 API에서 데이터 검색
4. 결과가 없는 경우 백업 데이터 활용
5. 검색 결과를 기반으로 LLM을 통해 응답 생성

예시 코드:

```python
# 전문가 클래스 내부 메서드
async def search_policy_database(self, keywords: List[str], policy_type: str = None) -> List[Dict[str, Any]]:
    try:
        # API 매니저를 통해 공공데이터 검색
        policy_cards = await self.api_manager.search_by_keywords(keywords, "정책")
        
        # 검색 결과가 있으면 반환
        if policy_cards:
            return policy_cards
            
        # 검색 결과가 없는 경우 백업 데이터 활용
        return [{
            "id": "policy1",
            "title": "장애인연금제도",
            "summary": "...",
            # ... 백업 데이터
        }]
    except Exception as e:
        logger.error(f"정책 검색 중 오류 발생: {e}")
        # 오류 발생 시 기본 데이터 반환
        return [백업_데이터]
```

## 오류 처리 및 fallback 메커니즘

시스템은 API 연동 중 오류 발생 시에도 서비스가 중단되지 않도록 여러 계층의 fallback 메커니즘을 구현하고 있습니다:

1. API 키 누락 시 - 백업 데이터 활용
2. API 요청 실패 시 - 다른 관련 API 시도
3. 모든 API 실패 시 - 전문가별 정적 백업 데이터 활용
4. 백업 데이터도 없는 경우 - 기본 응답 생성

## API 추가 및 확장 방법

새로운 공공데이터 API를 추가하고 싶다면 다음 단계를 따르세요:

1. `app/service/public_api/` 디렉토리에 새로운 API 클라이언트 파일 생성
2. `BaseApiClient` 클래스를 상속받아 API 클라이언트 클래스 구현
3. `ApiManager` 클래스에 새 API 클라이언트 등록
4. `.env.example` 파일에 새 API 키 변수 추가
5. 해당 API를 사용할 전문가 클래스 수정

---

## 참고 자료

- [공공데이터 포털](https://www.data.go.kr/)
- [한국장애인고용공단 API](https://www.kead.or.kr/view/service/service09_01.jsp)
- [Open API 활용 가이드](https://www.data.go.kr/ugs/selectPublicDataUseGuideView.do)
- [aiohttp 문서](https://docs.aiohttp.org/) 