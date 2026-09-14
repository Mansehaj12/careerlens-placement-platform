"""
Vector Database Manager for CareerLens AI
Manages persistent ChromaDB collections, batch upserts, and filtered vector similarity search.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


class CareerVectorStore:
    """
    Manages local persistent vector storage using ChromaDB with metadata filtering.
    """

    def __init__(self, persist_dir: str = r"data\chroma_db", collection_name: str = "career_docs"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        os.makedirs(self.persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        # Uses cosine distance by default or configured metadata
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]], batch_size: int = 250):
        """Batch upserts chunks and their embeddings into ChromaDB."""
        total = len(chunks)
        print(f"[*] Upserting {total} chunks into ChromaDB collection '{self.collection_name}'...")

        for i in range(0, total, batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]

            ids = [c["chunk_id"] for c in batch_chunks]
            documents = [c["text"] for c in batch_chunks]
            metadatas = [
                {
                    "doc_id": c["doc_id"],
                    "title": c["title"],
                    "company": c["company"],
                    "category": c["category"],
                    "location": c["location"],
                    "min_exp": float(c.get("min_exp", -1.0)),
                    "max_exp": float(c.get("max_exp", -1.0)),
                    "skills": c.get("skills", ""),
                    "section": c.get("section", "")
                }
                for c in batch_chunks
            ]

            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=batch_embeddings,
                metadatas=metadatas
            )
            print(f"  -> Processed {min(i + batch_size, total)}/{total} chunks.")

        print("[+] All chunks successfully indexed in ChromaDB.")

    def query_similarity(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes dense vector similarity search with optional metadata pre-filtering.
        Returns formatted result objects with similarity scores.
        """
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self.collection.query(**kwargs)

        hits = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                chunk_id = results["ids"][0][i]
                doc_text = results["documents"][0][i]
                meta = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                # In Chroma with cosine space: similarity = 1 - distance
                similarity_score = 1.0 - float(distance)

                hits.append({
                    "chunk_id": chunk_id,
                    "text": doc_text,
                    "metadata": meta,
                    "score": round(similarity_score, 4),
                    "retrieval_type": "dense"
                })

        return hits

    def count(self) -> int:
        """Returns the number of documents in the collection."""
        return self.collection.count()
