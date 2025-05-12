import os
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")

# API URL 구조 세부 내용 주석 추가
# 공공데이터 API URL 설정
ODCLOUD_API_BASE = os.getenv("ODCLOUD_API_BASE", "https://api.odcloud.kr/api")
APIS_DATA_API_BASE = os.getenv("APIS_DATA_API_BASE", "https://apis.data.go.kr")
API_DATA_BASE = os.getenv("API_DATA_BASE", "https://www.data.go.kr")

# 한국장애인고용공단 API 기본 경로
# B552583는 한국장애인고용공단의 기관코드입니다
KEAD_API_BASE = os.getenv("KEAD_API_BASE", "https://api.kead.or.kr")

# 한국장애인고용공단 API 엔드포인트 - 실시간 구인정보 관련
# 구인정보 API는 https://apis.data.go.kr/B552583/job 경로를 사용합니다
KEAD_JOB_API = f"{KEAD_API_BASE}/job"
KEAD_JOB_INFO_API = os.getenv("KEAD_JOB_INFO_API", f"{APIS_DATA_API_BASE}/B552583/disJbInfo")
KEAD_JOB_LIST_ENV_API = os.getenv("KEAD_JOB_LIST_ENV_API", f"{APIS_DATA_API_BASE}/B552583/job/getDisJbListEnv")
KEAD_JOB_LIST_INFO_API = os.getenv("KEAD_JOB_LIST_INFO_API", f"{APIS_DATA_API_BASE}/B552583/job/getDisJbList")
KEAD_JOB_DETAIL_API = os.getenv("KEAD_JOB_DETAIL_API", f"{APIS_DATA_API_BASE}/B552583/job/getDisJbDetail")

# 한국장애인고용공단 기타 API 엔드포인트
KEAD_STANDARD_COMPANY_API = f"{KEAD_API_BASE}/comp"  # 장애인 표준사업장 실시간 조회
KEAD_ASSISTIVE_DEVICE_API = f"{KEAD_API_BASE}/productlist"  # 보조공학기기 제품 정보
KEAD_SUPPORT_INSTITUTION_API = f"{KEAD_API_BASE}/instn"  # 근로지원인 수행기관 실시간 정보
KEAD_JOB_SEEKER_API = os.getenv("KEAD_JOB_SEEKER_API", "https://api.odcloud.kr/api")

# 장애인 관련 기타 API
DISABLED_ORGS_API = f"{API_DATA_BASE}/openapi/tn_pubr_public_disabled_orgs_api"  # 전국장애인단체표준데이터

# 복지로 API 설정
# 기존 URL (구버전 - 2025년 7월 이후 중지 예정)
BOKJIRO_API_BASE_OLD = os.getenv("BOKJIRO_API_BASE_OLD", "https://www.bokjiro.go.kr/openapi")
WELFARE_SERVICE_ENDPOINT_OLD = "service/v1/dis"  # 장애인 복지 서비스 정보 조회 (구버전)
WELFARE_DISCOUNT_ENDPOINT_OLD = "discount/v1/dis"  # 장애인 감면혜택 정보 조회 (구버전)
WELFARE_ACTIVITY_ENDPOINT_OLD = "activity/v1/dis"  # 장애인 활동지원 서비스 정보 조회 (구버전)

# 최신 복지로 API URL (2025년 4월 24일 공지사항 기준 변경된 URL)
BOKJIRO_API_BASE = os.getenv("BOKJIRO_API_BASE", "http://apis.data.go.kr/B554287/NationalWelfareInformationsV001")
WELFARE_SERVICE_LIST_ENDPOINT = "NationalWelfarelistV001"  # 복지서비스 목록조회 (최신)
WELFARE_SERVICE_DETAIL_ENDPOINT = "NationalWelfaredetailedV001"  # 복지서비스 상세조회 (최신)

# 복지로 웹사이트 URL
BOKJIRO_WEBSITE = "https://www.bokjiro.go.kr"

# 서비스 키 - 공단에서 발급받은 API 키 (환경변수에서 로드)
# 주의: SERVICE_KEY_IS_NOT_REGISTERED_ERROR가 발생한다면 
# 유효한 공공데이터포털 API 키가 환경변수에 설정되어 있는지 확인하세요
# 한국장애인고용공단 API에는 반드시 유효한 API 키가 필요합니다
ODCLOUD_SERVICE_KEY = os.getenv("ODCLOUD_SERVICE_KEY", "")  # 디코딩된 서비스키
ODCLOUD_SERVICE_KEY_ENC = os.getenv("ODCLOUD_SERVICE_KEY_ENC", "")  # 인코딩된 서비스키

# 로그에 키 설정 여부 출력
logging.getLogger(__name__).info(f"ODCLOUD_SERVICE_KEY 환경변수 설정됨: {bool(ODCLOUD_SERVICE_KEY)}")
logging.getLogger(__name__).info(f"ODCLOUD_SERVICE_KEY_ENC 환경변수 설정됨: {bool(ODCLOUD_SERVICE_KEY_ENC)}")

# 기관별 API 키 설정 (필요한 경우 개별 설정)
# 대부분의 경우 공통 키를 사용하므로 아래 변수들은 기본값으로 공통 키를 사용하도록 설정

WELFARE_API_KEY = os.getenv("WELFARE_API_KEY", "")
POLICY_API_KEY = os.getenv("POLICY_API_KEY", "")
MOEL_API_KEY = os.getenv("MOEL_API_KEY", ODCLOUD_SERVICE_KEY)  # 고용노동부
HRD_API_KEY = os.getenv("HRD_API_KEY", ODCLOUD_SERVICE_KEY)  # 한국산업인력공단
KOSHA_API_KEY = os.getenv("KOSHA_API_KEY", ODCLOUD_SERVICE_KEY)  # 안전보건공단
COMWEL_API_KEY = os.getenv("COMWEL_API_KEY", ODCLOUD_SERVICE_KEY)  # 근로복지공단
KEIS_API_KEY = os.getenv("KEIS_API_KEY", ODCLOUD_SERVICE_KEY)  # 한국고용정보원
KOSEA_API_KEY = os.getenv("KOSEA_API_KEY", ODCLOUD_SERVICE_KEY)  # 한국사회적기업진흥원
KODDI_API_KEY = os.getenv("KODDI_API_KEY", ODCLOUD_SERVICE_KEY)  # 한국장애인개발원

# API 요청시 공통으로 사용되는 파라미터
API_PARAMS = {
    'serviceKey': ODCLOUD_SERVICE_KEY
}

# API 요청시 공통으로 사용되는 헤더
API_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# 서버 설정
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

# 데이터베이스 설정
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "27017"))
DB_NAME = os.getenv("DB_NAME", "idea_ai")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# 데이터 설정
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
POLICY_DATA_FILE = os.path.join(DATA_DIR, "policies.json")

# 세션 설정
SESSION_SECRET = os.getenv("SESSION_SECRET", "my_secret_key")
SESSION_EXPIRE_DAYS = int(os.getenv("SESSION_EXPIRE_DAYS", "7"))

# MongoDB 설정
MONGODB_URL = os.getenv("MONGO_URI")

