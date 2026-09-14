"""
Index Builder for CareerLens AI
Loads chunked documents, builds BM25 sparse index, generates dense embeddings with SentenceTransformers,
and indexes everything into persistent ChromaDB.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vectorstore.embedder import DocumentEmbedder
from src.vectorstore.store import CareerVectorStore
from src.retrieval.bm25_retriever import CareerBM25Retriever

CHUNKS_FILE = r"data\processed\job_chunks.jsonl"
BM25_OUTPUT = r"data\bm25_index.pkl"
CHROMA_DIR = r"data\chroma_db"


def main():
    print(f"[*] Reading chunks from {CHUNKS_FILE}...")
    chunks = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    total = len(chunks)
    print(f"[+] Loaded {total} chunks.")

    # 1. Build & Save BM25 Index
    print("\n--- STEP 1: Building BM25 Sparse Keyword Index ---")
    bm25 = CareerBM25Retriever(chunks)
    bm25.save(BM25_OUTPUT)

    # 2. Build ChromaDB Vector Store
    print("\n--- STEP 2: Generating Dense Vectors & Indexing into ChromaDB ---")
    embedder = DocumentEmbedder()
    store = CareerVectorStore(persist_dir=CHROMA_DIR)

    # Extract text from chunks
    texts = [c["text"] for c in chunks]

    print(f"[*] Generating embeddings for {len(texts)} chunks using {embedder.model_name}...")
    # Generate embeddings in batches
    embeddings = embedder.embed_texts(texts, batch_size=64, show_progress_bar=True)

    print("[*] Storing in ChromaDB...")
    store.add_chunks(chunks, embeddings, batch_size=250)

    print(f"\n[+] SUCCESS! Indexed {store.count()} chunks in persistent ChromaDB at '{CHROMA_DIR}'.")
    print(f"[+] BM25 index persisted at '{BM25_OUTPUT}'.")


if __name__ == "__main__":
    main()
