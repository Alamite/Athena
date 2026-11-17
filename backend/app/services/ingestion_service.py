from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.database.vector_store import get_vector_store

async def ingest_document(file_path: str):

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
    )

    chunks = splitter.split_documents(documents)

    vector_store = get_vector_store()

    vector_store.add_documents(chunks)

    return len(chunks)
