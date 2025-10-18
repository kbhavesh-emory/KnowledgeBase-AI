# backend/scripts/setup.py
#!/usr/bin/env python3
"""
Setup script for KnowledgeBase-AI:
- Initializes SQLite storage
- Initializes RAG (embeddings + FAISS)
- Runs a quick embedding smoke test
"""

import argparse
import logging

from backend.config.logging import setup_logging        # absolute imports
from backend.core.rag import RAGSystem
from backend.core.storage import KnowledgeStorage

logger = logging.getLogger(__name__)


def setup_system() -> bool:
    """Initialize storage + RAG and run an embedding sanity test."""
    try:
        logger.info("🚀 Setting up KnowledgeBase-AI system...")

        storage = KnowledgeStorage()
        logger.info("✅ Knowledge storage initialized")

        rag = RAGSystem()
        logger.info("✅ RAG system initialized")

        test_texts = ["This is a test document for system setup."]
        embs = rag.embedding_manager.embed_texts(test_texts)
        logger.info(f"✅ Embedding test successful: shape={embs.shape}")

        logger.info("🎉 System setup completed successfully!")
        return True
    except Exception as e:
        logger.exception("❌ System setup failed")
        return False


def main():
    parser = argparse.ArgumentParser(description="KnowledgeBase-AI Setup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    setup_logging()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ok = setup_system()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
