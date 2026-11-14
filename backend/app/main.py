
from fastapi import FastAPI
from app.routers import chat

app = FastAPI(
    title="RAG Chatbot API",
    version="1.0.0"
)

app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "message": "RAG Chatbot API is running!"
    }
