from embeddings.embedder import Embedder
from vectorstore.chroma_store import ChromaStore


class Retriever:

    def __init__(self):
        self.embedder = Embedder()
        self.store = ChromaStore()

    def retrieve(self, query, top_k=5):
        query_embedding = self.embedder.embed([query])[0]

        results = self.store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        chunks = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, doc in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}

            if metadata is None:
                metadata = {}

            chunks.append(
                {
                    "id": metadata.get("chunk_id", f"unknown-{i}"),
                    "content": doc,
                    "metadata": metadata,
                    "distance": distances[i] if i < len(distances) else None,
                }
            )

        return chunks