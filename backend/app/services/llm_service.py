from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.core.config import settings


use_ollama = settings.USE_OLLAMA

if use_ollama.lower() == "true":
    llm = ChatOllama (
        model = settings.OLLAMA_MODEL,
        temperature = settings.TEMP
    )
else:
    llm = ChatOpenAI (
        model = settings.GPT_MODEL,
        temperature = settings.TEMP,
        api_key=settings.OPENAI_API_KEY
    )

async def generate_response(message: str) -> str:
    response = await llm.ainvoke(message)
    return response.content

def get_llm():
    return llm