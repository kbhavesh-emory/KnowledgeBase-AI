# backend/core/embeddings.py
import logging
from typing import List

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from backend.config.settings import settings  # absolute import

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """GPU-optimized embedding manager (P100-safe)."""

    def __init__(self):
        self.model: SentenceTransformer | None = None
        self.device: torch.device | None = None
        self._setup_device()
        self._load_model()

    def _setup_device(self) -> None:
        # Prefer CUDA if available (with P100-compatible torch)
        if torch.cuda.is_available() and str(settings.GPU_DEVICE).lower() == "cuda":
            self.device = torch.device("cuda")
            try:
                torch.backends.cudnn.benchmark = True
            except Exception:
                pass
            try:
                # available in recent torch; harmless if missing on older versions
                torch.set_float32_matmul_precision("medium")
            except Exception:
                pass
            logger.info(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device("cpu")
            logger.info("⚠️ Using CPU for embeddings")

    def _load_model(self) -> None:
        try:
            # SentenceTransformer accepts 'device' string ('cpu' or 'cuda')
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL, device=str(self.device))
            logger.info(f"✅ Loaded embedding model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0,), dtype=np.float32)

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=int(settings.EMBEDDING_BATCH_SIZE),
                show_progress_bar=False,
                normalize_embeddings=bool(settings.NORMALIZE_EMBEDDINGS),
                convert_to_numpy=True,
            )
            # Clear GPU cache to reduce fragmentation on 16GB P100
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            # Ensure float32 for FAISS
            if embeddings.dtype != np.float32:
                embeddings = embeddings.astype(np.float32, copy=False)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            if self.device and self.device.type == "cuda":
                logger.info("🔄 Falling back to CPU for embeddings")
                self.device = torch.device("cpu")
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL, device="cpu")
                return self.embed_texts(texts)
            raise

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed_texts([query])[0]
