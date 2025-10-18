# backend/api/routes/chat.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


# ==== Schemas ====

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[ChatMessage]] = None
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    message_id: str


class SaveRequest(BaseModel):
    question: str
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


# ==== helpers ====

def _services(request: Request):
    """
    Resolve long-lived singletons from FastAPI app.state.
    These are initialized in backend/api/main.py lifespan().
    """
    try:
        rag_system = request.app.state.rag_system
        chat_agent = request.app.state.chat_agent
        knowledge_storage = request.app.state.knowledge_storage
    except AttributeError as e:
        logger.exception("App state not initialized")
        raise HTTPException(status_code=500, detail="Server not initialized") from e
    return rag_system, chat_agent, knowledge_storage


# ==== Routes ====

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    Retrieve relevant chunks via RAG, build a numbered context,
    ask the LLM, and return the response with source metadata.
    """
    rag_system, chat_agent, _ = _services(request)
    try:
        logger.info("Chat request: %s", payload.message[:200])
        documents = rag_system.search(payload.message)

        # Build a numbered context so the LLM can cite [1], [2], ...
        numbered_context_parts: List[str] = []
        for i, d in enumerate(documents, start=1):
            src = d.metadata.get("source", "Unknown")
            snippet = d.page_content
            numbered_context_parts.append(f"[{i}] Source: {src}\n{snippet}")

        context = "\n\n".join(numbered_context_parts)

        response_text = chat_agent.generate_response(
            question=payload.message,
            context=context,
            chat_history=[m.model_dump() for m in (payload.chat_history or [])],
        )

        sources: List[Dict[str, Any]] = []
        for i, d in enumerate(documents, start=1):
            preview = d.page_content
            if len(preview) > 200:
                preview = preview[:200] + "..."
            sources.append(
                {
                    "index": i,
                    "source": d.metadata.get("source", "Unknown"),
                    "type": d.metadata.get("file_type", "text"),
                    "score": float(d.metadata.get("score", 0.0)),
                    "content_preview": preview,
                }
            )

        return ChatResponse(
            response=response_text,
            sources=sources,
            message_id=f"msg_{abs(hash(payload.message))}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/save")
async def save_response(request: Request, payload: SaveRequest):
    """
    Save a Q/A pair (with optional sources/tags) into the knowledge base.
    """
    _, __, storage = _services(request)
    try:
        rid = storage.save_response(
            question=payload.question,
            answer=payload.answer,
            sources=payload.sources or [],
            tags=payload.tags or [],
            model_used="llama3:latest",
        )
        return {"success": True, "message": "Response saved to knowledge base", "response_id": rid}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Save error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/saved")
async def get_saved_responses(request: Request, limit: int = 50, offset: int = 0):
    """
    List saved responses (most recent first).
    """
    _, __, storage = _services(request)
    try:
        data = storage.get_saved_responses(limit=limit, offset=offset)
        return {"responses": data, "count": len(data)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("List saved error")
        raise HTTPException(status_code=500, detail=str(e))
