import uuid

from ingestion.schema import Chunk
from ingestion.chunker import chunk_text


def process_documents(documents):

    all_chunks = []

    for doc in documents:

        text_chunks = chunk_text(doc["content"])

        for idx, chunk in enumerate(text_chunks):

            chunk_obj = Chunk(
                id=str(uuid.uuid4()),
                document_name=doc["document_name"],
                source=doc["source"],
                chunk_index=idx,
                content=chunk,
                metadata={}
            )

            all_chunks.append(chunk_obj)

    return all_chunks