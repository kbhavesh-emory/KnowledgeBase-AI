# backend/config/logging.py
"""
Centralized logging configuration for KnowledgeBase-AI.

- Creates logs/ directory before attaching file handlers (prevents startup crashes)
- Console + file logging with sane format
- Respects LOG_LEVEL env var (defaults to INFO)
- Avoids duplicate handlers on hot-reload (uvicorn --reload)
- Plays nicely with uvicorn/fastapi loggers
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


def _ensure_logs_dir(path: Path) -> None:
    """Create the logs directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def _coerce_level(level: Optional[str]) -> int:
    """Convert string level (e.g., 'DEBUG') to logging level int; default INFO."""
    if not level:
        return logging.INFO
    level = level.strip().upper()
    return getattr(logging, level, logging.INFO)


def setup_logging() -> None:
    """
    Initialize root logging with console + file handlers exactly once.
    Safe to call multiple times (idempotent).
    """
    root = logging.getLogger()
    # Idempotency: if handlers already exist, do nothing
    if getattr(root, "_kbai_init_done", False):
        return

    # Resolve log level from env (LOG_LEVEL) or default
    level = _coerce_level(os.getenv("LOG_LEVEL", "INFO"))

    # Ensure logs directory exists BEFORE creating FileHandler
    logs_dir = Path("logs")
    _ensure_logs_dir(logs_dir)
    log_file = logs_dir / "application.log"

    # Build formatter
    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_LOG_DATEFMT)

    # Console handler (stdout)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)

    # File handler (utf-8)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(formatter)

    # Configure root logger
    root.setLevel(level)
    root.handlers = [ch, fh]

    # Tame overly chatty libraries (optional, tune as needed)
    for noisy in ("urllib3", "httpx", "PIL", "asyncio"):
        logging.getLogger(noisy).setLevel(max(level, logging.WARNING))

    # Uvicorn/fastapi integration:
    # - Let uvicorn access/format go through our root format
    uvicorn_loggers = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "starlette",
    )
    for name in uvicorn_loggers:
        lg = logging.getLogger(name)
        lg.setLevel(level)
        # Do not add extra handlers to avoid duplicates; use root handlers
        lg.propagate = True

    # Mark as initialized
    root._kbai_init_done = True

    # Optional boot message
    logging.getLogger(__name__).info(
        "Logging initialized (level=%s, file=%s)", logging.getLevelName(level), str(log_file)
    )
