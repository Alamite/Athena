from langchain_chroma import Chroma

from app.core.config import settings
from app.services.embedding_service import get_embedding_model

vector_store = Chroma(
    collection_name = "rag_socuments",
    embedding_function = get_embedding_model(),
    persist_directory = settings.VECTOR_DB_PATH
)

def get_vector_store():
    return vector_store