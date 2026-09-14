"""
Dense Vector Retriever for CareerLens AI
Wraps DocumentEmbedder and CareerVectorStore for semantic search.
"""

from typing import List, Dict, Any, Optional
from src.vectorstore.embedder import DocumentEmbedder
from src.vectorstore.store import CareerVectorStore


class CareerDenseRetriever:
    """
    Dense semantic retriever searching over high-dimensional vector embeddings.
    """

    def __init__(self, embedder: DocumentEmbedder, store: CareerVectorStore):
        self.embedder = embedder
        self.store = store

    def search(
        self,
        query: str,
        top_k: int = 10,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Embeds query and retrieves nearest neighbors from vector store."""
        query_vector = self.embedder.embed_query(query)
        return self.store.query_similarity(query_vector, top_k=top_k, where_filter=where_filter)
