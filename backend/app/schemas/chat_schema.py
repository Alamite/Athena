from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str

class Source(BaseModel):
    source: str | None = None
    page: int |None = None
class ChatResponse(BaseModel):
    response: str
    sources: list[Source] = []