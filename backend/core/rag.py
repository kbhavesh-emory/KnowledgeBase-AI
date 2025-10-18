# backend/core/rag.py
import logging
from typing import Any, Dict, List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from backend.config.settings import settings  # absolute imports
from backend.core.embeddings import EmbeddingManager
from backend.vectorstore.manager import VectorStoreManager

logger = logging.getLogger(__name__)


class RAGSystem:
    """High-performance RAG system with GPU-accelerated embeddings + FAISS."""

    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.vector_store = VectorStoreManager(self.embedding_manager)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(settings.CHUNK_SIZE),
            chunk_overlap=int(settings.CHUNK_OVERLAP),
            separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],
        )

    def add_documents(self, documents: List[Document]) -> int:
        """Split and add to vector store."""
        if not documents:
            return 0
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} docs into {len(chunks)} chunks")
        return self.vector_store.add_documents(chunks)

    def search(self, query: str, k: int | None = None) -> List[Document]:
        """Retrieve top-k documents."""
        k = int(k or settings.RETRIEVE_K)
        return self.vector_store.search(query, k=k)

    def get_stats(self) -> Dict[str, Any]:
        return self.vector_store.get_stats()
