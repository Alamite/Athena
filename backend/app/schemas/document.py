from pydantic import BaseModel


class DocumentInfo(BaseModel):
    name: str
    chunks: int


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int
