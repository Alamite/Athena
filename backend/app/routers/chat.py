import asyncio
import json
import logging

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.rag_service import generate_rag_response, run_rag_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/chat",
    tags = ["chat"]
)

@router.post("/", response_model = ChatResponse)
async def chat(request: ChatRequest):

    result = await generate_rag_response(request.message, request.retrieval_type, request.k, request.use_reranker)

    return ChatResponse(
        response=result["response"],
        sources=result["sources"]
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Run the RAG pipeline and stream progress as newline-delimited JSON.

    Events:
      {"type": "step", "id", "label", "status": "running"|"done"|"error", "duration_ms"?, "detail"?}
      {"type": "result", "response", "sources", "chunks": [{"rank", "content", "metadata"}]}
      {"type": "error", "detail"}
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    # Called from both the event loop and the retrieval threadpool.
    def emit(event):
        loop.call_soon_threadsafe(queue.put_nowait, event)

    def on_step(step: dict):
        emit({"type": "step", **step})

    async def worker():
        try:
            result = await run_rag_pipeline(
                request.message,
                request.retrieval_type,
                request.k,
                request.use_reranker,
                on_step = on_step
            )
            emit({"type": "result", **result})
        except Exception as exc:
            logger.exception("Streaming chat failed")
            emit({"type": "error", "detail": f"{type(exc).__name__}: {str(exc)[:300]}"})
        finally:
            emit(None)

    async def event_stream():
        task = asyncio.create_task(worker())
        try:
            while (event := await queue.get()) is not None:
                yield json.dumps(jsonable_encoder(event)) + "\n"
        finally:
            # Client disconnected (e.g. pressed Stop): don't keep generating.
            task.cancel()

    return StreamingResponse(
        event_stream(),
        media_type = "application/x-ndjson",
        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
