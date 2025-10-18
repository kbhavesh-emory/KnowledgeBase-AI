# backend/ingest/processor.py
"""
FileProcessor: unified, robust file loader for KnowledgeBase-AI.

- Uses unstructured's auto-partition for rich docs (PDF/DOCX/PPTX/HTML/etc.)
- Uses fast text partition for plain-text/code
- Enforces max file size from settings
- Returns clean text suitable for chunking/embedding
"""

from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Optional

from unstructured.partition.auto import partition
from unstructured.partition.text import partition_text

from backend.config.settings import settings


TEXT_EXTS = {
    ".txt", ".md", ".rst", ".json", ".yaml", ".yml", ".xml",
    ".csv", ".html", ".htm", ".py", ".js", ".ts", ".java", ".cpp"
}

BINARY_OK = {
    ".pdf", ".docx", ".pptx", ".xlsx",
    ".doc", ".ppt", ".xls"
}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}


def _too_big(path: Path) -> bool:
    try:
        size_mb = path.stat().st_size / (1024 * 1024)
        return size_mb > float(settings.MAX_FILE_SIZE_MB)
    except Exception:
        return False


class FileProcessor:
    """Parses a single file path into plain text."""

    def __init__(self) -> None:
        self.max_mb = float(settings.MAX_FILE_SIZE_MB)

    def is_supported(self, path: Path) -> bool:
        ext = path.suffix.lower()
        return ext in TEXT_EXTS or ext in BINARY_OK

    def should_skip(self, path: Path) -> bool:
        parts = set(path.parts)
        return bool(parts & SKIP_DIRS)

    def load(self, path: Path) -> str:
        """
        Load a file and return text content.
        Uses unstructured for rich docs; falls back to raw read for text files.
        """
        ext = path.suffix.lower()
        if _too_big(path):
            return ""

        try:
            if ext in TEXT_EXTS:
                # Fast path for plain text/code
                try:
                    parts = partition_text(filename=str(path))
                    return "\n".join(el.text for el in parts if getattr(el, "text", "").strip())
                except Exception:
                    return path.read_text(encoding="utf-8", errors="ignore")

            # Rich docs via auto-partition
            if ext in BINARY_OK:
                elements = partition(filename=str(path))
                return "\n".join(el.text for el in elements if getattr(el, "text", "").strip())

            # If we get here, try plain read as a best effort
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            # Ultimate fallback
            try:
                return path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return ""
