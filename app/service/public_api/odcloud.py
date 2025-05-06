import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

def get_service_key(encoded=True):
    """
    환경 변수에서 서비스키를 가져온다.
    encoded=True면 인코딩 키, False면 디코딩 키를 반환
    """
    if encoded:
        key = os.getenv("ODCLOUD_SERVICE_KEY_ENC")
        if key:
            return key
    # fallback: 디코딩 키를 인코딩해서 사용
    key = os.getenv("ODCLOUD_SERVICE_KEY")
    return quote(key, safe='') if key else None

def get_disabled_job_seekers(page=1, per_page=10):
    """
    한국장애인고용공단_장애인 구직자 현황 API 호출
    """
    service_key = get_service_key(encoded=True)
    if not service_key:
        raise ValueError("ODCLOUD_SERVICE_KEY 또는 ODCLOUD_SERVICE_KEY_ENC가 .env에 설정되어 있지 않습니다.")
    url = (
        "https://api.odcloud.kr/api/15014774/v1/uddi:bed031bf-2d7b-40ee-abef-b8e8ea0b0467"
        f"?page={page}&perPage={per_page}&serviceKey={service_key}"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json() 