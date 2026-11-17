from langchain_ollama import OllamaEmbeddings

from app.core.config import settings

embeddings = OllamaEmbeddings(model = settings.EMBEDDING_MODEL)

def get_embedding_model():
    return embeddings
