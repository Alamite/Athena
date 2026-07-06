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
        final_k=5,
        on_event=None
    ):

        def emit(step, status, message, **data):
            if on_event:
                event = {"step": step, "status": status, "message": message}
                if data:
                    event["data"] = data
                on_event(event)

        emit(
            "rewrite_query", "start",
            "Rewriting query into alternate phrasings..."
        )
        rewrites = self.query_rewriter.rewrite(query)
        queries = [query] + rewrites
        emit(
            "rewrite_query", "done",
            f"Generated {len(rewrites)} alternative "
            f"quer{'y' if len(rewrites) == 1 else 'ies'}",
            queries=queries
        )

        emit(
            "vector_search", "start",
            f"Searching vector store (Chroma) across "
            f"{len(queries)} quer{'y' if len(queries) == 1 else 'ies'}..."
        )
        vector_lists = [
            self.vector.retrieve(q, top_k=retrieval_k)
            for q in queries
        ]
        vector_count = sum(len(r) for r in vector_lists)
        emit(
            "vector_search", "done",
            f"Vector search returned {vector_count} candidate matches"
        )

        emit(
            "bm25_search", "start",
            f"Searching BM25 keyword index across "
            f"{len(queries)} quer{'y' if len(queries) == 1 else 'ies'}..."
        )
        bm25_lists = [
            self.bm25.search(q, top_k=retrieval_k)
            for q in queries
        ]
        bm25_count = sum(len(r) for r in bm25_lists)
        emit(
            "bm25_search", "done",
            f"BM25 search returned {bm25_count} candidate matches"
        )

        emit(
            "fusion", "start",
            "Fusing vector + BM25 results via "
            "Reciprocal Rank Fusion..."
        )
        fused_results = reciprocal_rank_fusion(
            *vector_lists, *bm25_lists
        )
        emit(
            "fusion", "done",
            f"Fused into {len(fused_results)} unique candidate chunks"
        )

        emit(
            "rerank", "start",
            f"Reranking {len(fused_results)} candidates "
            "with cross-encoder (ms-marco-MiniLM-L-6-v2)..."
        )
        reranked_results = self.reranker.rerank(
            query,
            fused_results
        )
        top_results = reranked_results[:final_k]
        emit(
            "rerank", "done",
            f"Selected top {len(top_results)} chunks after reranking"
        )

        return top_results
