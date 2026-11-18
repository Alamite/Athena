from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    message: str
    retrieval_type: Literal[
        "similarity",
        "bm25",
        "hybrid_search"
    ] = "similarity"

class Source(BaseModel):
    source: str | None = None
    page: int |None = None
class ChatResponse(BaseModel):
    response: str
    sources: list[Source] = []