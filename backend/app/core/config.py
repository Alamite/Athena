from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

#base directory:
BASE_DIR = Path(__file__).resolve().parents[2]

class Settings:


    USE_OLLAMA = os.getenv("USE_OLLAMA", "True")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "OPENAI_API_KEY")

    TEMP = float(os.getenv("TEMP", "0.2"))

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:4b")

    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")

    COLLECTINO_NAME = os.getenv("COLLECTION_NAME", "rag_documents")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))

    MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE", str(10 * 1024 *1024))

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))

    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

settings = Settings()

#Ensure runtime directories are created:
Path(settings.UPLOAD_DIR).mkdir(parents = True, exist_ok = True)
Path(settings.VECTOR_DB_PATH).mkdir(parents = True, exist_ok = True)