from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from app.database.vector_store import get_vector_store
from app.services.reranking_service import rerank_documents


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

            fused_scores[doc_id] += 1 / (k + rank)

    ranked_documents = sorted(
        fused_scores,
        key = lambda doc_id: fused_scores[doc_id],
        reverse = True
    )

    return [
        document_map[doc_id]
        for doc_id in ranked_documents    
    ]


def retrieve_documents(query: str, k: int = 3, retrieval_type: str = "similarity", use_reranker: bool = False, candidate_k: int = 10):

    
    vector_store = get_vector_store()
    if retrieval_type == "similarity":
        

        documents = vector_store.similarity_search(
            query,
            k = k
        )

        return documents

    elif retrieval_type == "bm25":
        bm25_retriever = get_bm25_retriever(vector_store, k)

        if bm25_retriever is None:
            return []

        documents = bm25_retriever.invoke(query)

        return documents

    elif retrieval_type == "hybrid_search":


        vector_results = vector_store.similarity_search(
            query,
            k = candidate_k
        )

        bm25_retriever = get_bm25_retriever(vector_store, candidate_k)
        
        if bm25_retriever is None:
            return []

        bm25_results = bm25_retriever.invoke(query)

        combined_results = reciprocal_rank_fusion([vector_results, bm25_results])

        if use_reranker:
            reranked_results = rerank_documents(
                query = query,
                documents = combined_results,
                top_k = k
            )
            return reranked_results[:k]
        else:
            return combined_results[:k]

    else:
        raise ValueError(
            f"Unsupported retrieval type: {retrieval_type}"
        )
