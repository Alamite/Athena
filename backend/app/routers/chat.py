from fastapi import APIRouter

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import generate_response

router = APIRouter(
    prefix = "/chat",
    tags = ["chat"]
)

@router.post("/", response_model = ChatResponse)
async def chat(request: ChatRequest):

    response = await generate_response(request.message)

    return ChatResponse(
        response = response
    )