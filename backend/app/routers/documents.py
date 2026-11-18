import logging
import uuid

from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.schemas.document_schema import DocumentUploadResponse
from app.services.ingestion_service import ingest_document

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/documents",
    tags=["documents"]
)

@router.post("/upload",response_model = DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code = 400,
            detail = "Filename is required."
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code = 400,
            detail = "Only PDF files allowed."
        )


    content = await file.read()

    # if len(content) > settings.MAX_FILE_SIZE:
    #     raise HTTPException(
    #         status_code=413,
    #         detail="File exceeds the maximum upload size."
    #     )

    # 3. Validate PDF signature
    if b"%PDF-" not in content[:1024]:
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file."
        )

    #generate a safe filename to safe on the server.
    unique_filename = f"{uuid.uuid4().hex}.pdf"

    file_path = Path(settings.UPLOAD_DIR) / unique_filename

    try:

        #save uploaded file
        file_path.write_bytes(content)

        result = await run_in_threadpool(
            ingest_document,
            str(file_path),
            Path(file.filename).name
        )

        return DocumentUploadResponse(
            message="Document Indexed!",
            document_id= result["document_id"],
            filename= result["filename"],
            total_pages= result["total_pages"],
            total_chunks= result["total_chunks"]
        )
    
    except Exception as exc:

        # Remove uploaded file if ingestion fails
        file_path.unlink(missing_ok=True)

        logger.exception("Document ingestion failed")

        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Please try again."
        ) from exc

    finally:
        await file.close()
