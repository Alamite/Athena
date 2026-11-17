from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

#base directory:
BASE_DIR = Path(__file__).resolve().parents[2]

class Settings:

    MODEL = os.getenv("MODEL", "llama3.1:8b")
    TEMP = float(os.getenv("TEMP", "0.2"))

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:4b")

    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")

    COLLECTINO_NAME = os.getenv("COLLECTION_NAME", "rag_documents")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))

    MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE", str(10 * 1024 *1024))

settings = Settings()

#Ensure runtime directories are created:
Path(settings.UPLOAD_DIR).mkdir(parents = True, exist_ok = True)
Path(settings.VECTOR_DB_PATH).mkdir(parents = True, exist_ok = True)