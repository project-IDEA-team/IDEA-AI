import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()  # 반드시 인스턴스 생성 전에 호출

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_client():
    """
    OpenAI 클라이언트 인스턴스를 반환합니다.
    """
    return openai_client
