from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    question: str


class CitationItem(BaseModel):
    document: str
    chunk: int


class RetrievedChunk(BaseModel):
    document: str
    chunk: int
    score: float
    content: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem]
    retrieved_chunks: List[RetrievedChunk]
