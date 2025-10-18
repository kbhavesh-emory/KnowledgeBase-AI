# backend/vectorstore/manager.py
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
from langchain.schema import Document

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    FAISS vector store manager with persistence.

    - Lazily creates the FAISS index with the correct dimension based on the
      first batch of embeddings (so it doesn't require EMBEDDING_DIM ahead of time).
    - Persists index to VECTORSTORE_PATH/faiss.index and docs to documents.json.
    - Uses inner product (IP). If embeddings are not normalized by the encoder,
      we normalize here to ensure IP ~ cosine.
    """

    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager
        self.index: Optional[faiss.IndexFlat] = None
        self.documents: List[Document] = []
        self.vectorstore_path = Path(settings.VECTORSTORE_PATH)
        self.index_file = self.vectorstore_path / "faiss.index"
        self.docs_file = self.vectorstore_path / "documents.json"

        self.vectorstore_path.mkdir(parents=True, exist_ok=True)
        self._load_existing()

    # ---------- Persistence ----------

    def _load_existing(self) -> None:
        """Load existing FAISS index + docs if present."""
        loaded = False
        if self.index_file.exists():
            try:
                self.index = faiss.read_index(str(self.index_file))
                loaded = True
                logger.info("✅ Loaded existing FAISS index")
            except Exception as e:
                logger.warning(f"Failed to load FAISS index: {e}")

        if self.docs_file.exists():
            try:
                raw = json.loads(self.docs_file.read_text(encoding="utf-8"))
                self.documents = [
                    Document(page_content=item["page_content"], metadata=item.get("metadata", {}))
                    for item in raw
                ]
                logger.info(f"✅ Loaded {len(self.documents)} document chunks")
            except Exception as e:
                logger.warning(f"Failed to load documents.json: {e}")

        if not loaded:
            # Leave self.index=None; we will create it lazily when we see first embeddings
            logger.info("ℹ️ No existing FAISS index found; will create lazily on first add()")

    def _save_index(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_file))

    def _save_documents(self) -> None:
        data = [{"page_content": d.page_content, "metadata": d.metadata} for d in self.documents]
        self.docs_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # ---------- Core ops ----------

    def _ensure_index(self, dim: int) -> None:
        """Create a new FAISS index if we don't have one yet."""
        if self.index is None:
            self.index = faiss.IndexFlatIP(int(dim))
            logger.info(f"✅ Created new FAISS IndexFlatIP(dim={dim})")

    def add_documents(self, documents: List[Document]) -> int:
        """Add split LangChain Documents to the index."""
        if not documents:
            return 0

        texts = [d.page_content for d in documents]
        # Embed
        embeddings = self.embedding_manager.embed_texts(texts)
        if embeddings.size == 0:
            return 0

        # Ensure float32 for FAISS
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32, copy=False)

        # If NOT already normalized by encoder, normalize here for cosine via IP
        if not bool(settings.NORMALIZE_EMBEDDINGS):
            faiss.normalize_L2(embeddings)

        # Lazy index creation using embedding dimension
        emb_dim = int(embeddings.shape[1])
        self._ensure_index(emb_dim)

        # Add vectors
        self.index.add(embeddings)
        self.documents.extend(documents)

        # Persist
        self._save_index()
        self._save_documents()

        logger.info(f"✅ Added {len(documents)} chunks (total vectors={self.index.ntotal})")
        return len(documents)

    def search(self, query: str, k: int = 8) -> List[Document]:
        """Search for top-k similar chunks."""
        if self.index is None or self.index.ntotal == 0:
            return []

        q = self.embedding_manager.embed_query(query).astype(np.float32).reshape(1, -1)
        if not bool(settings.NORMALIZE_EMBEDDINGS):
            faiss.normalize_L2(q)

        scores, idxs = self.index.search(q, int(k))
        out: List[Document] = []
        for score, idx in zip(scores[0], idxs[0]):
            if 0 <= int(idx) < len(self.documents) and float(score) >= float(settings.SCORE_THRESHOLD):
                doc = self.documents[int(idx)]
                # ensure metadata dict exists and attach score
                meta = dict(doc.metadata or {})
                meta["score"] = float(score)
                doc.metadata = meta
                out.append(doc)
        return out

    def get_stats(self) -> Dict[str, Any]:
        dim = getattr(self.index, "d", None) if self.index is not None else None
        return {
            "document_count": int(self.index.ntotal) if self.index is not None else 0,
            "embedding_dim": int(dim) if dim is not None else None,
            "index_type": "FAISS (FlatIP)",
            "score_threshold": float(settings.SCORE_THRESHOLD),
        }
