# backend/core/storage.py
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from backend.config.settings import settings  # absolute import


class KnowledgeStorage:
    """SQLite-backed storage for saved responses, chat sessions, and metrics."""

    def __init__(self) -> None:
        self.db_path = Path(settings.PIXELTABLE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS saved_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    sources JSON,
                    model_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags JSON,
                    metadata JSON
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    title TEXT,
                    messages JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT,
                    value REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def save_response(
        self,
        question: str,
        answer: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        model_used: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO saved_responses
                (question, answer, sources, model_used, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    question,
                    answer,
                    json.dumps(sources or []),
                    model_used,
                    json.dumps(tags or []),
                    json.dumps({"saved_at": datetime.now().isoformat()}),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_saved_responses(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT * FROM saved_responses
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            return [dict(row) for row in cur.fetchall()]

    def delete_response(self, response_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("DELETE FROM saved_responses WHERE id = ?", (response_id,))
            conn.commit()
            return cur.rowcount > 0

    def export_to_dataframe(self) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql("SELECT * FROM saved_responses", conn)
