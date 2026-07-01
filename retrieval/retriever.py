from embeddings.embedder import Embedder
from vectorstore.chroma_store import ChromaStore


class Retriever:

    def __init__(self):
        self.embedder = Embedder()
        self.store = ChromaStore()

    def retrieve(
        self,
        query,
        top_k=5
    ):
        query_embedding = self.embedder.embed(
            [query]
        )[0]

        results = self.store.search(
            query_embedding=query_embedding,
            top_k=top_k
        )

        chunks = []

        for i, doc in enumerate(
            results["documents"][0]
        ):
            chunks.append(
                {
                    "content": doc,
                    "metadata":
                        results["metadatas"][0][i],
                    "distance":
                        results["distances"][0][i]
                }
            )

        return chunks