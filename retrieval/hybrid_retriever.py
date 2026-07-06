from retrieval.retriever import Retriever
from retrieval.bm25_retriever import BM25Retriever
from retrieval.fusion import reciprocal_rank_fusion
from retrieval.reranker import Reranker
from retrieval.query_expander import QueryRewriter


class HybridRetriever:

    def __init__(self):
        self.vector = Retriever()
        self.bm25 = BM25Retriever()
        self.reranker = Reranker()
        self.query_rewriter = QueryRewriter()

    def retrieve(
        self,
        query,
        retrieval_k=20,
        final_k=5
    ):

        queries = [query] + self.query_rewriter.rewrite(query)

        result_lists = []

        for q in queries:
            result_lists.append(
                self.vector.retrieve(q, top_k=retrieval_k)
            )
            result_lists.append(
                self.bm25.search(q, top_k=retrieval_k)
            )

        fused_results = reciprocal_rank_fusion(*result_lists)

        reranked_results = self.reranker.rerank(
            query,
            fused_results
        )

        return reranked_results[:final_k]
