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

    def answer_question(self, question: str, on_event=None) -> dict:
        def emit(step, status, message, **data):
            if on_event:
                event = {"step": step, "status": status, "message": message}
                if data:
                    event["data"] = data
                on_event(event)

        chunks = self.retriever.retrieve(question, on_event=on_event)

        if not chunks:
            emit(
                "generation", "done",
                "No relevant chunks found; skipping generation"
            )
            return {
                "answer": "I cannot answer based on the retrieved documents.",
                "citations": [],
                "retrieved_chunks": [],
            }

        emit(
            "build_context", "start",
            "Assembling context window from retrieved chunks..."
        )
        context = build_context(chunks)
        emit(
            "build_context", "done",
            f"Context assembled ({len(context)} characters)"
        )

        emit(
            "generation", "start",
            f"Generating answer with {self.generator.model} via Ollama..."
        )
        answer = self.generator.generate(question, context)
        emit("generation", "done", "Answer generated")

        emit("citations", "start", "Extracting source citations...")
        citations = generate_citations(chunks)
        emit(
            "citations", "done",
            f"Found {len(citations)} citation(s)"
        )

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
