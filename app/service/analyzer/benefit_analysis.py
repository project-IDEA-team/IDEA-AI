import os
import json
import pymysql
from pymongo import MongoClient
from dotenv import load_dotenv
from app.service.openai_client import get_client

# 환경변수 로드
load_dotenv()

# MongoDB 설정
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["kead_db"]
policy_collection = mongo_db["policy"]

# MySQL 설정
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB") 

# MySQL 연결 함수
def get_mysql_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# GPT 분석 및 저장 함수
async def analyze_and_store(user_info: dict, job_info: dict):
    client = get_client()

    # 🔎 MongoDB에서 정책 데이터 가져오기 (요약 + 세부내용을 묶어서)
    policies = list(policy_collection.find({"beneficiary_type": {"$in": ["individual", "company"]}}))
    policy_texts = []

    for p in policies:
        summary = p.get("summary", "")
        details = p.get("details", "")
        if isinstance(details, dict):
            detail_str = "\n".join([f"{k}: {v}" for k, v in details.items()])
        elif isinstance(details, list):
            detail_str = "\n".join(details)
        else:
            detail_str = str(details)
        policy_texts.append(f"{p.get('policy_name', '')}:\n{summary}\n{detail_str}")

    policy_text_combined = "\n\n".join(policy_texts)

    prompt = f"""
    유저 정보:
    {json.dumps(user_info, ensure_ascii=False)}

    공고 정보:
    {json.dumps(job_info, ensure_ascii=False)}

    아래는 관련 정책 목록입니다:
    {policy_text_combined}

    위 정책 중 유저와 기업에게 해당될 수 있는 혜택을 각각 뽑아서 요약해줘.

    형식:
    내 혜택:
    - 혜택1
    - 혜택2

    기업 혜택:
    - 혜택1
    - 혜택2
    """

    # GPT 호출
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "너는 장애인 정책 분석가야."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content

    # 결과 파싱
    lines = content.splitlines()
    my_benefits, company_benefits = [], []
    current = None
    for line in lines:
        if "내 혜택" in line:
            current = "user"
            continue
        elif "기업 혜택" in line:
            current = "company"
            continue
        if line.startswith("-"):
            if current == "user":
                my_benefits.append(line.lstrip("- ").strip())
            elif current == "company":
                company_benefits.append(line.lstrip("- ").strip())

    # MySQL 저장
    conn = get_mysql_connection()
    with conn.cursor() as cursor:
        sql = """
        INSERT INTO analysis_results (user_id, job_id, my_benefits, company_benefits)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            my_benefits = VALUES(my_benefits),
            company_benefits = VALUES(company_benefits)
        """
        cursor.execute(sql, (
            user_info["id"],
            job_info["jobId"],
            "\n".join(my_benefits),
            "\n".join(company_benefits)
        ))
        conn.commit()
    conn.close()

    return {
        "my_benefits": my_benefits,
        "company_benefits": company_benefits
    }
