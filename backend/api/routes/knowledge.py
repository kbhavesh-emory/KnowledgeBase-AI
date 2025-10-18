# backend/api/routes/knowledge.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from langchain.schema import Document

from backend.config.settings import settings
from backend.ingest.files import FileManager

router = APIRouter()
logger = logging.getLogger(__name__)


def _services(request: Request):
    try:
        rag_system = request.app.state.rag_system
        storage = request.app.state.knowledge_storage
        return rag_system, storage
    except AttributeError as e:
        raise HTTPException(status_code=500, detail="Server not initialized") from e


@router.get("/knowledge/stats")
async def knowledge_stats(request: Request):
    rag, storage = _services(request)
    try:
        stats = rag.get_stats()
        return {"vectorstore": stats}
    except Exception as e:
        logger.exception("stats error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/upload")
async def upload_document(request: Request, file: UploadFile = File(...)):
    """
    Upload a document and add it to the vector store.
    """
    rag, _ = _services(request)
    try:
        # Save to data/documents
        doc_dir = Path("data/documents")
        doc_dir.mkdir(parents=True, exist_ok=True)
        dst = doc_dir / file.filename
        content = await file.read()
        dst.write_bytes(content)

        # Ingest incrementally
        fm = FileManager()
        docs = fm.process_directory_incremental(str(doc_dir))
        added = rag.add_documents(docs) if docs else 0

        return {"success": True, "added_chunks": added, "path": str(dst)}
    except Exception as e:
        logger.exception("upload error")
        raise HTTPException(status_code=500, detail=str(e))
