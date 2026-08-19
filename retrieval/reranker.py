from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(self, query, chunks):

        valid_chunks = [
            chunk
            for chunk in chunks
            if isinstance(chunk.get("content"), str)
            and chunk["content"].strip()
        ]

        if not valid_chunks:
            return []

        pairs = [
            (
                query,
                chunk["content"]
            )
            for chunk in valid_chunks
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(valid_chunks, scores),
            key=lambda x: float(x[1]),
            reverse=True
        )

        return [
            {
                **chunk,
                "rerank_score": float(score)
            }
            for chunk, score in ranked
        ]