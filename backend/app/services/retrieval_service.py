import time
from contextlib import contextmanager
from typing import Callable

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from app.database.vector_store import get_vector_store
from app.services.reranking_service import rerank_documents


# Optional callback that receives pipeline progress events, e.g.
# {"id": "vector_search", "label": "Vector search", "status": "done", "duration_ms": 41.2, "detail": "10 candidates"}
StepCallback = Callable[[dict], None] | None


@contextmanager
def pipeline_step(on_step: StepCallback, step_id: str, label: str):
    """Time a pipeline stage and report running/done/error to `on_step`.

    The body can set `info["detail"]` to attach a short summary to the done event.
    """
    info = {"detail": None}

    if on_step:
        on_step({"id": step_id, "label": label, "status": "running"})

    start = time.perf_counter()

    try:
        yield info
    except Exception as exc:
        if on_step:
            on_step({
                "id": step_id,
                "label": label,
                "status": "error",
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
                "detail": str(exc)[:200],
            })
        raise

    if on_step:
        on_step({
            "id": step_id,
            "label": label,
            "status": "done",
            "duration_ms": round((time.perf_counter() - start) * 1000, 1),
            "detail": info["detail"],
        })


def get_bm25_retriever(vector_store, k: int):
    stored_data = vector_store.get(
        include = ["documents", "metadatas"]
    )

    documents = [
        Document(
            page_content = content,
            metadata = metadata or {}
        )
        for content, metadata in zip(
            stored_data["documents"] or [],
            stored_data["metadatas"] or []
        )
    ]

    if not documents:
        return None

    return BM25Retriever.from_documents(
        documents,
        k=k
    )

def reciprocal_rank_fusion(results: list[list[Document]],k: int = 60):

    fused_scores = {}
    document_map = {}

    for result in results:

        for rank, doc in enumerate(result, start=1):

            doc_id = (
                doc.metadata.get("document_id"),
                doc.metadata.get("chunk_index"),
                doc.page_content
            )

            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0
                document_map[doc_id] = doc
            else:
                # Same chunk found by both retrievers: keep the ranks/scores each one recorded.
                document_map[doc_id].metadata.update({
                    key: value
                    for key, value in doc.metadata.items()
                    if key not in document_map[doc_id].metadata
                })

            fused_scores[doc_id] += 1 / (k + rank)

    ranked_documents = sorted(
        fused_scores,
        key = lambda doc_id: fused_scores[doc_id],
        reverse = True
    )

    for doc_id in ranked_documents:
        document_map[doc_id].metadata["rrf_score"] = round(fused_scores[doc_id], 5)

    return [
        document_map[doc_id]
        for doc_id in ranked_documents    
    ]


def _vector_search(vector_store, query: str, k: int, on_step: StepCallback):
    with pipeline_step(on_step, "vector_search", "Vector search") as info:
        results = vector_store.similarity_search_with_score(query, k = k)

        documents = []
        for rank, (doc, distance) in enumerate(results, start = 1):
            doc.metadata["vector_rank"] = rank
            doc.metadata["vector_distance"] = round(float(distance), 4)
            documents.append(doc)

        info["detail"] = f"{len(documents)} candidates by embedding similarity"
        return documents


def _bm25_search(vector_store, query: str, k: int, on_step: StepCallback):
    with pipeline_step(on_step, "bm25_search", "BM25 keyword search") as info:
        bm25_retriever = get_bm25_retriever(vector_store, k)

        if bm25_retriever is None:
            info["detail"] = "Index is empty"
            return None

        documents = bm25_retriever.invoke(query)

        for rank, doc in enumerate(documents, start = 1):
            doc.metadata["bm25_rank"] = rank

        info["detail"] = f"{len(documents)} candidates by keyword match"
        return documents


def retrieve_documents(query: str, k: int = 3, retrieval_type: str = "similarity", use_reranker: bool = False, candidate_k: int = 10, on_step: StepCallback = None):

    
    vector_store = get_vector_store()
    if retrieval_type == "similarity":

        return _vector_search(vector_store, query, k, on_step)

    elif retrieval_type == "bm25":

        documents = _bm25_search(vector_store, query, k, on_step)

        return documents or []

    elif retrieval_type == "hybrid_search":

        vector_results = _vector_search(vector_store, query, candidate_k, on_step)

        bm25_results = _bm25_search(vector_store, query, candidate_k, on_step)
        
        if bm25_results is None:
            return []

        with pipeline_step(on_step, "fusion", "Reciprocal rank fusion") as info:
            combined_results = reciprocal_rank_fusion([vector_results, bm25_results])
            info["detail"] = f"{len(combined_results)} unique chunks merged"

        if use_reranker:
            with pipeline_step(on_step, "rerank", "Cross-encoder reranking") as info:
                reranked_results = rerank_documents(
                    query = query,
                    documents = combined_results,
                    top_k = k
                )
                info["detail"] = f"Re-scored {len(combined_results)}, kept top {len(reranked_results[:k])}"
            return reranked_results[:k]
        else:
            return combined_results[:k]

    else:
        raise ValueError(
            f"Unsupported retrieval type: {retrieval_type}"
        )
