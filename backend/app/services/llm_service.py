from langchain_ollama import ChatOllama

from app.core.config import settings

model = settings.MODEL
temp = settings.TEMP

llm = ChatOllama (
    model = "llama3.1:8b",
    temperature = 0.2
)

async def generate_response(message: str) -> str:
    response = await llm.ainvoke(message)
    return response.content

def get_llm():
    return llm