import faiss
import numpy as np
import logging
from typing import List, Tuple
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class FAISSWrapper:
    """Enhanced FAISS wrapper with persistence and metadata"""
    
    def __init__(self, dimension: int, index_path: Path):
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = index_path.parent / "metadata.json"
        self.index = None
        self.metadata = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                
                logger.info(f"✅ Loaded FAISS index with {len(self.metadata)} documents")
                
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create new FAISS index"""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        logger.info("✅ Created new FAISS index")
    
    def add_vectors(self, vectors: np.ndarray, metadatas: List[dict]) -> int:
        """Add vectors with metadata to index"""
        if len(vectors) != len(metadatas):
            raise ValueError("Vectors and metadata must have same length")
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add to index
        self.index.add(vectors.astype(np.float32))
        
        # Add metadata
        start_idx = len(self.metadata)
        for i, metadata in enumerate(metadatas):
            self.metadata.append({
                **metadata,
                "vector_id": start_idx + i
            })
        
        self._save_index()
        
        return len(metadatas)
    
    def search(self, query_vector: np.ndarray, k: int = 8, score_threshold: float = 0.5) -> List[Tuple[dict, float]]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            return []
        
        # Normalize query vector
        query_vector = query_vector.reshape(1, -1).astype(np.float32)
        faiss.normalize_L2(query_vector)
        
        # Search
        scores, indices = self.index.search(query_vector, k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self.metadata) and score >= score_threshold:
                results.append((self.metadata[idx], float(score)))
        
        return results
    
    def _save_index(self):
        """Save index and metadata to disk"""
        faiss.write_index(self.index, str(self.index_path))
        
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_stats(self) -> dict:
        """Get index statistics"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": "FAISS (FlatIP)",
            "metadata_count": len(self.metadata)
        }
    
    def delete_vectors(self, vector_ids: List[int]) -> int:
        """Delete vectors by IDs (not implemented for Flat index)"""
        logger.warning("Delete operation not supported for Flat index")
        return 0