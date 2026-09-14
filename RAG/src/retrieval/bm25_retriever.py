"""
BM25 Sparse Keyword Retriever for CareerLens AI
Provides exact keyword matching for technical terminology, framework versions, and role titles.
"""

import re
import pickle
import os
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi


class CareerBM25Retriever:
    """
    Sparse keyword retriever using BM25Okapi.
    Specialized tokenizer preserves technical terms like 'c++', 'c#', 'ci/cd', 'node.js'.
    """

    def __init__(self, chunks: Optional[List[Dict[str, Any]]] = None):
        self.chunks = chunks or []
        self.bm25: Optional[BM25Okapi] = None
        if self.chunks:
            self._build_index()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tech-aware tokenization: preserves punctuation in tech keywords."""
        if not text:
            return []
        # Lowercase and match words or tech terms like c++, c#, .net, ci/cd
        tokens = re.findall(r"[a-zA-Z0-9+#\.\-]+", text.lower())
        # Filter out purely isolated punctuation
        return [t for t in tokens if len(t) > 1 or t in ["c", "r"]]

    def _build_index(self):
        print(f"[*] Building BM25 index over {len(self.chunks)} chunks...")
        corpus = [self.tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(corpus)
        print("[+] BM25 index built successfully.")

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Searches BM25 index and returns top-K hits with raw scores."""
        if not self.bm25 or not self.chunks:
            return []

        tokens = self.tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        hits = []
        for idx in top_indices:
            score = scores[idx]
            if score <= 0:
                continue
            chunk = self.chunks[idx]
            hits.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": {
                    "doc_id": chunk["doc_id"],
                    "title": chunk["title"],
                    "company": chunk["company"],
                    "category": chunk["category"],
                    "location": chunk["location"],
                    "min_exp": chunk.get("min_exp", -1.0),
                    "max_exp": chunk.get("max_exp", -1.0),
                    "skills": chunk.get("skills", ""),
                    "section": chunk.get("section", "")
                },
                "score": round(float(score), 4),
                "retrieval_type": "bm25"
            })

        return hits

    def save(self, filepath: str = r"data\bm25_index.pkl"):
        """Serializes the BM25 index and chunks for fast reload."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({"chunks": self.chunks, "bm25": self.bm25}, f)
        print(f"[+] Saved BM25 index to {filepath}")

    @classmethod
    def load(cls, filepath: str = r"data\bm25_index.pkl") -> "CareerBM25Retriever":
        """Loads serialized BM25 index."""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        instance = cls()
        instance.chunks = data["chunks"]
        instance.bm25 = data["bm25"]
        return instance
