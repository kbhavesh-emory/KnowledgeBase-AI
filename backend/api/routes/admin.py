# backend/api/routes/admin.py
from __future__ import annotations

import logging
import platform
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()
logger = logging.getLogger(__name__)


def _services(request: Request):
    try:
        rag_system = request.app.state.rag_system
        storage = request.app.state.knowledge_storage
        return rag_system, storage
    except AttributeError as e:
        raise HTTPException(status_code=500, detail="Server not initialized") from e


@router.get("/admin/status")
async def admin_status(request: Request):
    """
    Basic system status: CPU, RAM, Disk, and vectorstore stats.
    """
    rag, _ = _services(request)
    try:
        vm = psutil.virtual_memory()
        disk = shutil.disk_usage("/")
        status = {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "memory": {
                "total_gb": round(vm.total / (1024**3), 2),
                "used_gb": round(vm.used / (1024**3), 2),
                "percent": vm.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": round(100 * disk.used / disk.total, 2),
            },
            "vectorstore": rag.get_stats(),
        }
        return status
    except Exception as e:
        logger.exception("admin status error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/index/stats")
async def index_stats(request: Request):
    rag, _ = _services(request)
    try:
        return rag.get_stats()
    except Exception as e:
        logger.exception("index stats error")
        raise HTTPException(status_code=500, detail=str(e))
