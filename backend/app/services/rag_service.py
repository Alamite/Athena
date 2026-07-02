import logging
from typing import Optional

from backend.app.config import ROOT_DIR

logger = logging.getLogger(__name__)

# Import after config ensures sys.path is set
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.context_builder import build_context
from generation.answer_generator import AnswerGenerator
from generation.citations import generate_citations


class RAGService:

    def __init__(self):
        self._retriever: Optional[HybridRetriever] = None
        self._generator: Optional[AnswerGenerator] = None

    @property
    def retriever(self) -> HybridRetriever:
        if self._retriever is None:
            logger.info("Initializing HybridRetriever (this may take a moment)...")
            self._retriever = HybridRetriever()
        return self._retriever

    @property
    def generator(self) -> AnswerGenerator:
        if self._generator is None:
            self._generator = AnswerGenerator()
        return self._generator

    def reload(self):
        """Drop the cached retriever so it rebuilds with the latest chunks on next use."""
        self._retriever = None
        logger.info("RAGService: retriever will reload on next request")

    def answer_question(self, question: str) -> dict:
        chunks = self.retriever.retrieve(question)

        if not chunks:
            return {
                "answer": "I cannot answer based on the retrieved documents.",
                "citations": [],
                "retrieved_chunks": [],
            }

        context = build_context(chunks)
        answer = self.generator.generate(question, context)
        citations = generate_citations(chunks)

        retrieved_chunks = [
            {
                "document": c["metadata"]["document_name"],
                "chunk": c["metadata"]["chunk_index"],
                "score": round(float(c.get("rerank_score", 0.0)), 4),
                "content": c["content"],
            }
            for c in chunks
        ]

        return {
            "answer": answer,
            "citations": citations,
            "retrieved_chunks": retrieved_chunks,
        }


_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
