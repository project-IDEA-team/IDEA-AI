import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()  # 반드시 인스턴스 생성 전에 호출

# 클라이언트 설정
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1",  # 기본 URL 명시적 설정
    max_retries=2,  # 재시도 횟수 설정
    timeout=60.0  # 타임아웃 설정
)

def get_client():
    """
    OpenAI 클라이언트 인스턴스를 반환합니다.
    """
    return openai_client
