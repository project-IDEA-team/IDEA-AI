from fastapi import FastAPI
from app.router import chatbot

app = FastAPI()
app.include_router(chatbot.router)
