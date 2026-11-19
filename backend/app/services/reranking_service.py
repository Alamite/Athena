from sentence_transformers import CrossEncoder
from app.core.config import settings

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(
            "BAAI/bge-reranker-base",
            device = "cpu"
        )

    return _reranker

def rerank_documents(query: str, documents: list, top_k: int = 3):
    if not documents:
        return []

    reranker = get_reranker()

    pairs = [
        (query, document.page_content)
        for document in documents
    ]

    #Calculate relevance scores
    scores = reranker.predict(pairs)

    #preserve original documents and their scores
    ranked_results = []

    for original_rank, (document, score) in enumerate(
        zip(documents, scores),
        start = 1
    ):
        document = document.model_copy(deep=True)

        document.metadata["reranker_score"] = float(score)
        document.metadata["pre_rerank_score"] = original_rank

        ranked_results.append([document, float(score)])

    ranked_results.sort(
        key = lambda item: item[1],
        reverse = True
    )

    return [
        document
        for document, score in ranked_results[:top_k]
    ]