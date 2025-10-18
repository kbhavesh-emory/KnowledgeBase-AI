# backend/api/main.py
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.chat import router as chat_router
from backend.api.routes.knowledge import router as knowledge_router
from backend.api.routes.admin import router as admin_router
from backend.config.logging import setup_logging
from backend.config.settings import settings
from backend.core.agent import ChatAgent
from backend.core.rag import RAGSystem
from backend.core.storage import KnowledgeStorage

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Initializing KnowledgeBase-AI ...")
    try:
        app.state.rag_system = RAGSystem()
        app.state.knowledge_storage = KnowledgeStorage()
        app.state.chat_agent = ChatAgent()
        logger.info("✅ System initialized")
    except Exception:
        logger.exception("❌ Initialization failed")
        raise

    yield

    logger.info("🛑 Shutting down KnowledgeBase-AI ...")


app = FastAPI(
    title="KnowledgeBase AI",
    description="GPU-accelerated RAG system with Ollama integration",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
allowed: List[str] = settings.ALLOWED_ORIGINS or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(knowledge_router, prefix="/api/v1", tags=["knowledge"])
app.include_router(admin_router, prefix="/api/v1", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "KnowledgeBase AI API", "version": "2.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rag_system": "initialized" if getattr(app.state, "rag_system", None) else "not_initialized",
        "knowledge_storage": "initialized" if getattr(app.state, "knowledge_storage", None) else "not_initialized",
        "chat_agent": "initialized" if getattr(app.state, "chat_agent", None) else "not_initialized",
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
