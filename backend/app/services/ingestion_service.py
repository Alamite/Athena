import json
import logging
from pathlib import Path
from typing import List, Optional

from backend.app.config import (
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    CHUNKS_FILE,
    CHROMA_DIR,
)

# Import after config ensures sys.path is set
from ingestion.pipeline import process_documents
from embeddings.embedder import Embedder
from vectorstore.chroma_store import ChromaStore

logger = logging.getLogger(__name__)


class IngestionService:

    def __init__(self):
        self.embedder = Embedder()
        self.store = ChromaStore(persist_directory=str(CHROMA_DIR))

    def ingest_file(self, filename: str, content: bytes) -> int:
        """Save an uploaded .md file, chunk it, embed it, and update ChromaDB.

        Returns the number of new chunks created.
        """
        DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
        DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        file_path = DATA_RAW_DIR / filename
        file_path.write_bytes(content)

        document_name = Path(filename).stem

        doc = {
            "document_name": document_name,
            "source": str(file_path),
            "content": file_path.read_text(encoding="utf-8"),
        }

        new_chunks = process_documents([doc])
        new_chunks_dicts = [c.to_dict() for c in new_chunks]

        # Reload existing chunks and replace this document's entries
        existing_chunks: List[dict] = []
        if CHUNKS_FILE.exists():
            with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                existing_chunks = json.load(f)

        existing_chunks = [
            c for c in existing_chunks if c["document_name"] != document_name
        ]
        all_chunks = existing_chunks + new_chunks_dicts

        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(all_chunks)} total chunks to {CHUNKS_FILE}")

        # Remove stale ChromaDB entries for this document
        try:
            self.store.collection.delete(where={"document_name": document_name})
        except Exception:
            pass  # Collection may be empty; delete is best-effort

        # Embed and index new chunks
        texts = [c["content"] for c in new_chunks_dicts]
        logger.info(f"Embedding {len(texts)} chunks for '{document_name}'...")
        embeddings = self.embedder.embed(texts)

        self.store.add_documents(
            ids=[c["id"] for c in new_chunks_dicts],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {
                    "document_name": c["document_name"],
                    "source": c["source"],
                    "chunk_index": c["chunk_index"],
                    "chunk_id": c["id"],
                }
                for c in new_chunks_dicts
            ],
        )

        logger.info(f"Indexed {len(new_chunks)} chunks for '{document_name}'")
        return len(new_chunks)

    def list_documents(self) -> List[dict]:
        if not CHUNKS_FILE.exists():
            return []

        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        counts: dict = {}
        for chunk in chunks:
            name = chunk["document_name"]
            counts[name] = counts.get(name, 0) + 1

        return [{"name": name, "chunks": count} for name, count in counts.items()]


_ingestion_service: Optional[IngestionService] = None


def get_ingestion_service() -> IngestionService:
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
