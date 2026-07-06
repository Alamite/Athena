import asyncio
import json
import logging
import threading

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = await run_in_threadpool(
            get_rag_service().answer_question, request.question
        )
    except Exception as e:
        logger.exception("RAG pipeline failed")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")

    return ChatResponse(**result)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Same pipeline as /chat, but emits Server-Sent Events for each
    retrieval/generation stage before the final answer event."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    loop = asyncio.get_running_loop()
    events: asyncio.Queue = asyncio.Queue()

    def on_event(event: dict):
        loop.call_soon_threadsafe(events.put_nowait, event)

    def worker():
        try:
            result = get_rag_service().answer_question(
                request.question, on_event=on_event
            )
            loop.call_soon_threadsafe(
                events.put_nowait, {"step": "final", "status": "done", "data": result}
            )
        except Exception as e:
            logger.exception("RAG pipeline failed")
            loop.call_soon_threadsafe(
                events.put_nowait,
                {"step": "error", "status": "error", "message": str(e)},
            )
        finally:
            loop.call_soon_threadsafe(events.put_nowait, None)

    threading.Thread(target=worker, daemon=True).start()

    async def event_stream():
        while True:
            event = await events.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
