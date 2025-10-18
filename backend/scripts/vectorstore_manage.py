#!/usr/bin/env python3
"""
Vector store management utilities.

Usage:
  # Show stats
  python -m backend.scripts.vectorstore_manage stats

  # Test a query (top-k)
  python -m backend.scripts.vectorstore_manage query --q "how to start server" --k 5

  # Wipe index (danger!)
  python -m backend.scripts.vectorstore_manage wipe

  # Rebuild from documents and repositories (combo)
  python -m backend.scripts.vectorstore_manage rebuild \
      --docs data/documents --repos data/repositories
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from backend.config.logging import setup_logging
from backend.config.settings import settings
from backend.core.rag import RAGSystem
from backend.core.embeddings import EmbeddingManager
from backend.vectorstore.manager import VectorStoreManager
from langchain.schema import Document

def cmd_stats():
    rag = RAGSystem()
    stats = rag.get_stats()
    print(json.dumps(stats, indent=2))

def cmd_query(q: str, k: int):
    rag = RAGSystem()
    results: List[Document] = rag.search(q, k=k)
    print(f"\nTop {k} for: {q!r}\n")
    for i, d in enumerate(results, 1):
        score = d.metadata.get("score", 0.0)
        print(f"[{i}] {d.metadata.get('source')}  (score={score:.4f})")
        preview = d.page_content.strip().splitlines()
        snippet = " ".join(preview[:3])[:220]
        print(f"    {snippet}\n")

def cmd_wipe():
    """
    Remove FAISS index files and doc cache under VECTORSTORE_PATH.
    """
    base = Path(settings.VECTORSTORE_PATH).resolve()
    idx = base / "faiss.index"
    docs = base / "documents.json"
    removed = []
    for p in (idx, docs):
        if p.exists():
            p.unlink()
            removed.append(str(p))
    print("Removed:", removed if removed else "nothing to remove")

def cmd_rebuild(docs_path: str, repos_path: str):
    """
    Rebuild by clearing the index and running both document + repo embeddings.
    """
    cmd_wipe()
    # Recreate fresh managers (ensures new index file)
    emb = EmbeddingManager()
    vs = VectorStoreManager(emb)
    # Use RAGSystem to leverage chunking & add flow
    rag = RAGSystem()
    print("Rebuilding: embedding documents...")
    # Lazy import the sibling scripts so we don't duplicate logic
    from backend.scripts.embed_documents import load_directory
    from backend.scripts.embed_repositories import load_repo_files
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # documents
    doc_dir = Path(docs_path).resolve()
    doc_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],
    )
    rag.text_splitter = doc_splitter
    docs = load_directory(doc_dir, "**/*")
    if docs:
        added = rag.add_documents(docs)
        print(f"  + docs chunks: {added}")

    # repositories
    print("Rebuilding: embedding repositories...")
    code_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=600, chunk_overlap=80,
        separators=["\nclass ", "\ndef ", "\nasync def ", "\nfunction ", "\nexport ", "\nconst ", "\nlet ", "\nvar ", "\n\n", "\n", " ", ""],
    )
    rag.text_splitter = code_splitter
    repo_root = Path(repos_path).resolve()
    all_code_docs: List[Document] = []
    for sub in sorted([p for p in repo_root.iterdir() if p.is_dir()]):
        all_code_docs.extend(load_repo_files(sub, "**/*"))
    if all_code_docs:
        added = rag.add_documents(all_code_docs)
        print(f"  + code chunks: {added}")

    print("✅ Rebuild complete.")
    print(json.dumps(rag.get_stats(), indent=2))

def main():
    setup_logging()
    log = logging.getLogger(__name__)

    p = argparse.ArgumentParser(description="Vector store management")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats", help="Show vector store stats")

    q = sub.add_parser("query", help="Test a query against the store")
    q.add_argument("--q", required=True, help="Query text")
    q.add_argument("--k", type=int, default=settings.RETRIEVE_K, help="Top-K results")

    sub.add_parser("wipe", help="Delete FAISS index and document cache")

    r = sub.add_parser("rebuild", help="Wipe and rebuild from docs+repos")
    r.add_argument("--docs", default="data/documents", help="Documents path")
    r.add_argument("--repos", default="data/repositories", help="Repositories path")

    args = p.parse_args()

    if args.cmd == "stats":
        cmd_stats()
    elif args.cmd == "query":
        cmd_query(args.q, args.k)
    elif args.cmd == "wipe":
        cmd_wipe()
    elif args.cmd == "rebuild":
        cmd_rebuild(args.docs, args.repos)
    else:
        log.error("Unknown command")

if __name__ == "__main__":
    main()
