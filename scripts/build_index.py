import json

from embeddings.embedder import Embedder
from vectorstore.chroma_store import ChromaStore


def main():

    with open(
        "data/processed/chunks.json",
        "r",
        encoding="utf-8"
    ) as f:
        chunks = json.load(f)

    texts = [chunk["content"] for chunk in chunks]

    embedder = Embedder()

    print("Generating embeddings...")

    embeddings = embedder.embed(texts)

    print(f"Generated {len(embeddings)} embeddings")

    store = ChromaStore()

    ids = [chunk["id"] for chunk in chunks]

    documents = [
        chunk["content"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "document_name": chunk["document_name"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "chunk_id": chunk["id"]
        }
        for chunk in chunks
    ]

    store.add_documents(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print("Indexing complete")


if __name__ == "__main__":
    main()