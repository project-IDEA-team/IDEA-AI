# Python 3.12 베이스 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출 (애플리케이션이 사용하는 포트로 변경하세요)
EXPOSE 8000

# 애플리케이션 실행 명령 (실제 진입점 파일명으로 변경하세요)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]