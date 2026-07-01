import json

from rank_bm25 import BM25Okapi

class BM25Retriever:

    def __init__(
        self,
        chunks_path="data/processed/chunks.json"
    ):

        with open(
            chunks_path,
            "r",
            encoding="utf-8"
        ) as f:

            self.chunks = json.load(f)

        self.corpus = [
            chunk["content"]
            for chunk in self.chunks
        ]

        tokenized_corpus = [
            doc.lower().split()
            for doc in self.corpus
        ]

        self.bm25 = BM25Okapi(
            tokenized_corpus
        )

    def search(
    self,
    query,
    top_k=10
    ):

        tokens = query.lower().split()

        scores = self.bm25.get_scores(
            tokens
        )

        ranked = sorted(
            zip(self.chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )
        results = []
        for chunk, score in ranked[:top_k]:

            results.append(
                {
                    "id": chunk["id"],
                    "content": chunk["content"],
                    "metadata": {
                        "document_name":
                            chunk["document_name"],
                        "source":
                            chunk["source"],
                        "chunk_index":
                            chunk["chunk_index"]
                    },
                    "bm25_score": score
                }
            )

        return results