from fastapi import FastAPI
from app.router import chatbot

app = FastAPI()
app.include_router(chatbot.router)

@app.get("/")
def root():
    return {"message": "API is working"}
