from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    MODEL = os.getenv("MODEL", "llama3.1:8b")
    TEMP = float(os.getenv("TEMP", "0.2"))

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:4b")

    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    
settings = Settings()