from pydantic import BaseModel

class DocumentUploadResponse(BaseModel):

    message: str
    document_id: str
    filename: str
    total_pages: int
    total_chunks: int
    chunk_size: int
    chunk_overlap: int