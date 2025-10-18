#!/usr/bin/env python3
"""
Embed code from repositories into the vector store.

Usage:
  python -m backend.scripts.embed_repositories --repos data/repositories --glob "**/*"
  python -m backend.scripts.embed_repositories --repos /abs/repos --glob "**/*.{py,js,ts,md}"
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List

# project root on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backend.config.logging import setup_logging
from backend.config.settings import settings
from backend.core.rag import RAGSystem
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cpp", ".cc", ".c", ".h", ".hpp",
    ".php", ".rb", ".kt", ".scala", ".cs", ".sh", ".bash", ".ps1",
    ".sql", ".xml", ".yaml", ".yml", ".json", ".md", ".rst"
}

def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def load_repo_files(root: Path, glob: str) -> List[Document]:
    files = [p for p in root.glob(glob) if p.is_file()]
    files = [p for p in files if p.suffix.lower() in CODE_EXTS]
    docs: List[Document] = []
    for p in files:
        text = read_file(p)
        if not text.strip():
            continue
        docs.append(Document(
            page_content=text,
            metadata={
                "source": str(p),
                "file_type": p.suffix.lower() or "text",
                "repo_root": str(root)
            }
        ))
    return docs

def main():
    parser = argparse.ArgumentParser(description="Embed repositories (code) into vector store")
    parser.add_argument("--repos", type=str, default="data/repositories", help="Root directory with cloned repos")
    parser.add_argument("--glob", type=str, default="**/*", help="Glob for files to include")
    parser.add_argument("--chunk-size", type=int, default=600, help="Code chunk size (slightly larger)")
    parser.add_argument("--chunk-overlap", type=int, default=80, help="Code chunk overlap")
    args = parser.parse_args()

    setup_logging()
    log = logging.getLogger(__name__)
    root = Path(args.repos).resolve()
    if not root.exists():
        log.error(f"Repo path does not exist: {root}")
        sys.exit(1)

    log.info(f"🚀 Embedding repositories from {root}  (glob={args.glob})")

    # code-aware splitter: favor smaller separators first for cleaner chunks
    code_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        separators=[
            "\nclass ", "\ndef ", "\nasync def ", "\nfunction ", "\nexport ", "\nconst ", "\nlet ", "\nvar ",
            "\n\n", "\n", " ", ""
        ],
    )

    rag = RAGSystem()
    rag.text_splitter = code_splitter

    # gather across all repos (subfolders)
    all_docs: List[Document] = []
    for sub in sorted([p for p in root.iterdir() if p.is_dir()]):
        docs = load_repo_files(sub, args.glob)
        if docs:
            all_docs.extend(docs)
            log.info(f"  • {sub.name}: {len(docs)} files")

    if not all_docs:
        log.warning("No repository files found to embed.")
        return

    added = rag.add_documents(all_docs)
    stats = rag.get_stats()
    log.info(f"✅ Added {added} code chunks")
    log.info(f"📊 Stats: {stats}")

if __name__ == "__main__":
    main()
