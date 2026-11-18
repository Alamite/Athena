from fastapi import APIRouter

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import generate_response
from app.services.rag_service import generate_rag_response

router = APIRouter(
    prefix = "/chat",
    tags = ["chat"]
)

@router.post("/", response_model = ChatResponse)
async def chat(request: ChatRequest):

    result = await generate_rag_response(request.message, request.retrieval_type, request.k)

    return ChatResponse(
        response=result["response"],
        sources=result["sources"]
    )