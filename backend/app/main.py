
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import ChatOllama

app = FastAPI(
    title="RAG Chatbot API",
    version="1.0.0"
)

# Initialize Ollama LLM
llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.1
)


# Request schema
class ChatRequest(BaseModel):
    message: str


# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):

    response = await llm.ainvoke(request.message)

    return {
        "response": response.content
    }


@app.get("/")
async def root():
    return {
        "message": "RAG Chatbot API is running!"
    }
