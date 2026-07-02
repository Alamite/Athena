import logging
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from backend.app.schemas.document import DocumentInfo, UploadResponse
from backend.app.services.ingestion_service import get_ingestion_service
from backend.app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files are supported")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        chunks_created = await run_in_threadpool(
            get_ingestion_service().ingest_file, file.filename, content
        )
    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    # Reload retriever so BM25 picks up the new chunks
    get_rag_service().reload()

    return UploadResponse(
        message="Document ingested successfully",
        filename=file.filename,
        chunks_created=chunks_created,
    )


@router.get("", response_model=List[DocumentInfo])
async def list_documents():
    return get_ingestion_service().list_documents()
