from pathlib import Path
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.database.vector_store import get_vector_store

def ingest_document(file_path: str, original_filename: str, chunk_size: int = 1000, chunk_overlap: int = 150):

    with open(file_path, "rb") as file:
        file_hash = hashlib.sha256(file.read()).hexdigest()

    document_id = file_hash

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap
    )

    chunks = splitter.split_documents(documents)

    # Add metadata to chunks
    for index, chunk in enumerate(chunks):
        chunk.metadata.update({
            "document_id": document_id,
            "filename": original_filename,
            "chunk_index": index 
        })

    # Create unique chunk ids
    chunk_ids = [
        f"{document_id}_{index}"
        for index in range(len(chunks))
    ]

    vector_store = get_vector_store()

    # Remove previous chunks if the same document was already indexed.
    vector_store.delete(
        where = {
            "document_id": document_id
        }
    )

    BATCH_SIZE = 32

    for start in range(0, len(chunks), BATCH_SIZE):

        end = start + BATCH_SIZE

        batch_chunks = chunks[start:end]
        batch_ids = chunk_ids[start:end]

        vector_store.add_documents(
            documents=batch_chunks,
            ids=batch_ids
        )
    # Add the chunks to vector DB
    # vector_store.add_documents(
    #     documents = chunks,
    #     ids = chunk_ids
    # )

    return {
        "document_id": document_id,
        "filename": original_filename,
        "total_pages": len(documents),
        "total_chunks": len(chunks)
    }
