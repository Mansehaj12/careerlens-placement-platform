"""
Embedding Engine for CareerLens AI
Uses SentenceTransformers (all-MiniLM-L6-v2) to generate 384-dimensional dense semantic vectors.
"""

from typing import List, Union
import numpy as np


class DocumentEmbedder:
    """
    Bi-Encoder wrapper generating dense vector representations for queries and document chunks.
    Standard model: sentence-transformers/all-MiniLM-L6-v2 (384 dims, fast CPU inference).
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            print(f"[*] Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            print("[+] Embedding model loaded successfully.")
        return self._model

    def embed_texts(self, texts: List[str], batch_size: int = 32, show_progress_bar: bool = False) -> List[List[float]]:
        """Embeds a list of document strings into a list of vector floats."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=True,  # Crucial: cosine similarity equals dot product when normalized!
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single search query."""
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding.tolist()
