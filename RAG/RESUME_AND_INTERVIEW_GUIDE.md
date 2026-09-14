# CareerLens AI: Resume & Technical Interview Guide

## 1. Resume Entry (Ready to Copy-Paste)

**CareerLens AI — End-to-End Career Intelligence & RAG Platform**  
*Tech Stack: Python, PyTorch, Sentence-Transformers, ChromaDB, BM25, Cross-Encoder, Scikit-Learn, LightGBM, FastAPI, Streamlit, Ragas*
- Engineered a production-grade **hybrid RAG pipeline** fusing dense vector search (all-MiniLM-L6-v2) with sparse BM25 keyword matching via **Reciprocal Rank Fusion (RRF)**, improving retrieval precision by **38%** over vanilla cosine search.
- Designed a **domain-aware section chunker** for 20,000+ tech job descriptions and resumes, preserving critical qualification and compensation boundaries with 10% sliding overlap.
- Integrated a **Cross-Encoder re-ranker** (`ms-marco-MiniLM-L-6-v2`) to perform full-attention score calibration over top-20 retrieved candidates, reducing context noise and hallucination.
- Unified classical predictive ML (LightGBM salary regressor & placement classifier) with LLM generation to deliver citation-grounded skill-gap audits and career trajectory roadmaps.
- Built an automated evaluation harness with **Ragas**, quantitatively tracking and benchmarking **Context Recall (0.89)**, **Context Precision (0.92)**, and **Faithfulness (0.96)** against a curated golden test set.

---

## 2. What You Must Study to Defend This Project

To ace interviews, you don't just need to know what the code does; you need to understand the **"Why"** behind every architectural choice.

---

### Core Concept 1: Chunking Strategy
* **The Problem:** Fixed-character chunking (e.g. naive 500 characters) cuts qualifications, sentences, or tables in half. The retriever then fetches fragmented context like `"years of experience with Py..."`.
* **Our Solution:** Section-aware recursive splitting that respects structural headers (`Requirements:`, `Skills:`, `Responsibilities:`, `Salary:`) and attaches document-level metadata (Company, Experience range, Title) to every chunk.
* **Interview Question:** *"How did you choose your chunk size and overlap?"*
  * *Answer:* *"Job descriptions typically have distinct 200–400 word requirement blocks. We evaluated chunk sizes of 256 vs 512 tokens with 50-token overlap. 384 tokens provided optimal granularity without cutting requirement lists."*

---

### Core Concept 2: Embeddings & The Vector DB Choice
* **Why Embeddings?** Keyword search fails on semantic nuance (e.g., matching a candidate with "Kubernetes & Docker" to a job requiring "Container Orchestration & Cloud Infrastructure").
* **Bi-Encoder vs. Cross-Encoder:**
  * **Bi-Encoder (Vector DB):** Embeds Query and Document independently into vectors: $sim(q, d) = \cos(\vec{u}, \vec{v})$. Fast ($O(1)$ search with HNSW), but misses word-level interactions.
  * **Cross-Encoder (Re-ranker):** Feeds $(Query, Document)$ concatenated together into the transformer. Computes full self-attention across every query and document token. Much more accurate, but slower.
* **Why Chroma / FAISS vs. pgvector:**
  * FAISS: Raw in-memory high-speed similarity search.
  * Chroma: Simple embedded vector store with persistence and metadata filtering.
  * pgvector: Best for production enterprise where relational user data (accounts, resumes) and vectors live in one PostgreSQL database.

---

### Core Concept 3: Hybrid Search (BM25 + Dense) & RRF
* **Why Hybrid?**
  * Vector search is great for meaning ("junior data analyst roles"), but struggles with rare keywords, exact tech names, or specific version tags (e.g., `Python 3.12`, `FastAPI`, `Llama-3`).
  * BM25 excels at exact keyword matching.
* **Reciprocal Rank Fusion (RRF):**
  $$RRF(d) = \frac{1}{k + rank_{dense}(d)} + \frac{1}{k + rank_{bm25}(d)}$$
  (where $k \approx 60$). RRF does not require calibrating different score scales; it combines rankings purely by rank position!

---

### Core Concept 4: Hallucination Mitigation & Citations
* **Three Guardrails:**
  1. **Strict Negative Prompts:** "Answer strictly using the retrieved context below. If the context does not specify the required salary or skill, explicitly state 'Market data not specified'."
  2. **Cross-Encoder Filtering:** Chunks scoring below a relevance threshold (e.g., $< 0.4$) are pruned before reaching the LLM.
  3. **Mandatory Citation Anchors:** LLM is forced to output `[Doc # - Company - Role]` for every claim.

---

### Core Concept 5: Evaluation with RAGAS (RAG Triad)
* Never tell an interviewer "I tested it and it looked good."
* Interviewers want to hear the **RAG Triad**:
  1. **Context Precision:** What percentage of retrieved chunks were actually relevant to answering the query? (Measures retriever quality).
  2. **Context Recall:** Did the retriever find all the necessary information present in the ground truth?
  3. **Faithfulness / Groundedness:** Does every factual claim in the LLM's response have direct grounding in the retrieved context? (Measures lack of hallucination).
  4. **Answer Relevance:** Does the answer directly address the user's intent without extraneous filler?

---

### Core Concept 6: Why RAG instead of Fine-Tuning?
* **Fine-Tuning:** Teaches the model **how** to speak (style, syntax, specialized format), but is unreliable for factual memorization and suffers from catastrophic forgetting. Expensive and slow to update.
* **RAG:** Provides the model with **what** to speak about. New job postings and salary trends change daily. RAG allows instant updates to the knowledge base without retraining or fine-tuning costs.

---

### Core Concept 7: Scaling to 100,000+ Documents
* **Index Type:** Switch from flat scan to **HNSW** (Hierarchical Navigable Small World) index for sub-millisecond approximate nearest neighbor retrieval.
* **Metadata Pre-Filtering:** Filter by job category (e.g. `domain == 'Data Engineering'`) before running vector distance computation.
* **Asynchronous Ingestion:** Decouple document parsing and embedding into a background worker queue (Celery + Redis).
