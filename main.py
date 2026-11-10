from dotenv import load_dotenv
import os

import langchain_core
import langgraph
from langchain_ollama import ChatOllama

load_dotenv()

MODEL = os.getenv("MODEL")

def main() :
    llm = ChatOllama(
    model=MODEL,
    temperature=0,
    )
    response = llm.invoke(f"SETUP COMPLETE!")
    print(response)


if __name__ == "__main__":
    main()