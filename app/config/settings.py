import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")

# 공공데이터 API 키 설정
KEAD_API_KEY = os.getenv("KEAD_API_KEY", "")  # 한국장애인고용공단
WELFARE_API_KEY = os.getenv("WELFARE_API_KEY", "")  # 복지로
POLICY_API_KEY = os.getenv("POLICY_API_KEY", "")  # 정부24
MOEL_API_KEY = os.getenv("MOEL_API_KEY", "")  # 고용노동부
HRD_API_KEY = os.getenv("HRD_API_KEY", "")  # 한국산업인력공단
KOSHA_API_KEY = os.getenv("KOSHA_API_KEY", "")  # 안전보건공단
COMWEL_API_KEY = os.getenv("COMWEL_API_KEY", "")  # 근로복지공단
KEIS_API_KEY = os.getenv("KEIS_API_KEY", "")  # 한국고용정보원
KOSEA_API_KEY = os.getenv("KOSEA_API_KEY", "")  # 한국사회적기업진흥원
KODDI_API_KEY = os.getenv("KODDI_API_KEY", "")  # 한국장애인개발원

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