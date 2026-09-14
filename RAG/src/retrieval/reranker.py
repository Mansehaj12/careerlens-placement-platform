"""
Cross-Encoder Re-Ranking Engine for CareerLens AI
Performs joint full-attention scoring on (Query, Document) pairs to eliminate retrieval noise.
"""

from typing import List, Dict, Any


class CareerCrossEncoderReranker:
    """
    Cross-Encoder re-ranker using cross-encoder/ms-marco-MiniLM-L-6-v2.
    Takes candidate chunks retrieved by Hybrid search and calculates calibrated relevance probabilities.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            print(f"[*] Loading cross-encoder model: {self.model_name}...")
            self._model = CrossEncoder(self.model_name)
            print("[+] Cross-encoder model loaded successfully.")
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 4,
        score_threshold: float = -10.0  # Optional minimum logit cutoff
    ) -> List[Dict[str, Any]]:
        """
        Pairs query with each candidate text, runs cross-attention inference,
        and returns top_k candidates sorted by cross-encoder score.
        """
        if not candidates:
            return []

        # Create pairs: (query, text)
        pairs = [[query, c["text"]] for c in candidates]

        # Compute cross-encoder scores (logits)
        scores = self.model.predict(pairs)

        scored_candidates = []
        for i, cand in enumerate(candidates):
            score = float(scores[i])
            if score >= score_threshold:
                c_copy = dict(cand)
                c_copy["rerank_score"] = round(score, 4)
                c_copy["prior_score"] = cand.get("score")
                scored_candidates.append(c_copy)

        # Sort descending by reranker score
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_candidates[:top_k]
