"""
Hybrid Retrieval Engine for CareerLens AI
Fuses Dense Vector Search and BM25 Sparse Keyword Search using Reciprocal Rank Fusion (RRF).
"""

from typing import List, Dict, Any, Optional
from src.retrieval.dense_retriever import CareerDenseRetriever
from src.retrieval.bm25_retriever import CareerBM25Retriever


class CareerHybridRetriever:
    """
    Hybrid retriever combining semantic dense search and sparse BM25 keyword matching.
    Uses Reciprocal Rank Fusion (RRF) to merge rankings without arbitrary score normalization.
    """

    def __init__(
        self,
        dense_retriever: CareerDenseRetriever,
        bm25_retriever: CareerBM25Retriever,
        rrf_k: int = 60
    ):
        self.dense = dense_retriever
        self.bm25 = bm25_retriever
        self.rrf_k = rrf_k  # Standard RRF constant from Cormack et al. (SIGIR 2009)

    def search(
        self,
        query: str,
        top_k: int = 10,
        candidate_pool_size: int = 25,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        1. Retrieves candidate_pool_size hits from Dense retriever.
        2. Retrieves candidate_pool_size hits from BM25 retriever.
        3. Computes Reciprocal Rank Fusion (RRF) score for each unique chunk.
        4. Returns top_k fused results.
        """
        dense_hits = self.dense.search(query, top_k=candidate_pool_size, where_filter=where_filter)
        bm25_hits = self.bm25.search(query, top_k=candidate_pool_size)

        # Store maps of chunk_id -> chunk data
        chunk_map = {}
        rrf_scores = {}

        # 1. Process Dense ranks
        for rank, hit in enumerate(dense_hits):
            cid = hit["chunk_id"]
            chunk_map[cid] = hit
            # RRF formula: 1 / (k + rank)  (rank is 1-indexed)
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + (rank + 1)))

        # 2. Process BM25 ranks
        for rank, hit in enumerate(bm25_hits):
            cid = hit["chunk_id"]
            if cid not in chunk_map:
                chunk_map[cid] = hit
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + (rank + 1)))

        # 3. Sort by fused RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:top_k]

        fused_results = []
        for cid in sorted_cids:
            item = dict(chunk_map[cid])
            item["score"] = round(rrf_scores[cid], 5)
            item["retrieval_type"] = "hybrid_rrf"
            fused_results.append(item)

        return fused_results
