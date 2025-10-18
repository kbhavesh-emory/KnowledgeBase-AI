#!/usr/bin/env python3
"""
Embed plain documents from a directory into the vector store.

Usage:
  python -m backend.scripts.embed_documents --path data/documents --glob "**/*"
  python -m backend.scripts.embed_documents --path /abs/path/to/docs --glob "**/*.pdf" --batch-size 64
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backend.config.logging import setup_logging
from backend.config.settings import settings
from backend.core.rag import RAGSystem
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# ---------------------- loaders ---------------------- #

SUPPORTED_EXTS = {
    ".txt", ".md", ".rst", ".pdf", ".doc", ".docx", ".ppt", ".pptx",
    ".xls", ".xlsx", ".html", ".htm", ".xml", ".csv", ".json", ".yaml", ".yml"
}

def load_file(path: Path) -> List[Document]:
    """Load a single file with Unstructured loader."""
    try:
        loader = UnstructuredFileLoader(str(path), mode="elements")
        docs = loader.load()
        # normalize to langchain.schema.Document and attach metadata
        out = []
        for d in docs:
            out.append(Document(
                page_content=d.page_content,
                metadata={
                    "source": str(path),
                    "file_type": path.suffix.lower() or "text"
                }
            ))
        return out
    except Exception as e:
        logging.getLogger(__name__).warning(f"Skip {path} ({e})")
        return []

def load_directory(dir_path: Path, glob: str) -> List[Document]:
    files = [p for p in dir_path.glob(glob) if p.is_file()]
    files = [p for p in files if p.suffix.lower() in SUPPORTED_EXTS or not p.suffix]
    docs: List[Document] = []
    for p in files:
        docs.extend(load_file(p))
    return docs

# ---------------------- main flow ---------------------- #

def main():
    parser = argparse.ArgumentParser(description="Embed documents into vector store")
    parser.add_argument("--path", type=str, default="data/documents", help="Directory containing documents")
    parser.add_argument("--glob", type=str, default="**/*", help="Glob pattern for files")
    parser.add_argument("--batch-size", type=int, default=settings.EMBEDDING_BATCH_SIZE, help="Embedding batch size")
    parser.add_argument("--chunk-size", type=int, default=settings.CHUNK_SIZE, help="Chunk size")
    parser.add_argument("--chunk-overlap", type=int, default=settings.CHUNK_OVERLAP, help="Chunk overlap")
    args = parser.parse_args()

    setup_logging()
    log = logging.getLogger(__name__)
    log.info("🚀 Embedding documents...")
    log.info(f"Path={args.path}  glob={args.glob}")

    # allow overriding batch size at runtime
    os.environ["KB_EMBED_BATCH"] = str(args.batch_size)

    rag = RAGSystem()
    # override splitter for this run
    rag.text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],
    )

    docs = load_directory(Path(args.path).resolve(), args.glob)
    if not docs:
        log.warning("No documents found to embed.")
        return

    added = rag.add_documents(docs)
    stats = rag.get_stats()
    log.info(f"✅ Added {added} chunks")
    log.info(f"📊 Stats: {stats}")

if __name__ == "__main__":
    main()
