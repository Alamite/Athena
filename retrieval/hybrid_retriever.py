from retrieval.retriever import Retriever
from retrieval.bm25_retriever import BM25Retriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker


class HybridRetriever:

    def __init__(self):
        self.vector = Retriever()
        self.bm25 = BM25Retriever()
        self.reranker = Reranker()

    def retrieve(
        self,
        query,
        retrieval_k=20,
        final_k=5
    ):

        vector_results = self.vector.retrieve(
            query,
            top_k=retrieval_k
        )

        bm25_results = self.bm25.search(
            query,
            top_k=retrieval_k
        )

        fused_results = reciprocal_rank_fusion(
            vector_results,
            bm25_results
        )

        reranked_results = self.reranker.rerank(
            query,
            fused_results
        )

        return reranked_results[:final_k]