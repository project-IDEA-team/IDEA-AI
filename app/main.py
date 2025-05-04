from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import chatbot

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 개발 중이면 ["*"]로 모두 허용 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot.router)

@app.get("/")
def root():
    return {"message": "API is working"}
