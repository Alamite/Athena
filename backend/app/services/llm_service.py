from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os

MODEL = os.getenv("MODEL")
TEMP = os.getenv("TEMP")

llm = ChatOllama (
    model = "llama3.1:8b",
    temperature = 0.2
)

async def generate_response(message: str) -> str:
    response = await llm.ainvoke(message)
    return response.content
