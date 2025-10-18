# backend/ingest/files.py
"""
FileManager: directory crawler + incremental ingestion for KnowledgeBase-AI.

- Skips temp/system dirs
- Deduplicates via MD5 hash manifest (JSON)
- Returns LangChain Documents ready for chunking/embedding
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

from langchain.schema import Document

from backend.config.settings import settings
from backend.ingest.processor import FileProcessor

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
MANIFEST_NAME = "ingest_manifest.json"


def md5_file(path: Path, block_size: int = 1 << 20) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        while True:
            b = f.read(block_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


class FileManager:
    def __init__(self) -> None:
        self.proc = FileProcessor()
        # store manifest alongside vectorstore for convenience
        self.vector_dir = Path(settings.VECTORSTORE_PATH)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.vector_dir / MANIFEST_NAME
        self.manifest = self._load_manifest()

    # --------- Manifest ---------
    def _load_manifest(self) -> Dict:
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"files": {}}

    def _save_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")

    # --------- Discovery ---------
    def _iter_files(self, root: Path):
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            # skip system/large/unsupported
            if self.proc.should_skip(p):
                continue
            if not self.proc.is_supported(p):
                continue
            yield p

    # --------- Public API ---------
    def process_directory_incremental(self, root_dir: str | Path) -> List[Document]:
        root = Path(root_dir).resolve()
        if not root.exists():
            return []

        to_add: List[Document] = []
        files_entry: Dict[str, Dict] = self.manifest.get("files", {})

        for p in self._iter_files(root):
            try:
                h = md5_file(p)
            except Exception:
                continue

            rec = files_entry.get(str(p))
            if rec and rec.get("md5") == h:
                # unchanged
                continue

            # parse file to text
            text = self.proc.load(p).strip()
            if not text:
                continue

            meta = {"source": str(p), "file_type": p.suffix.lower()}
            to_add.append(Document(page_content=text, metadata=meta))
            files_entry[str(p)] = {"md5": h}

        # persist updated manifest
        self.manifest["files"] = files_entry
        self._save_manifest()
        return to_add

    def get_processing_stats(self) -> Dict[str, int]:
        files_entry = self.manifest.get("files", {})
        return {"tracked_files": len(files_entry)}
