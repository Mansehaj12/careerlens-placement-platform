# CareerLens AI — Complete Step-by-Step Build Log (A to Z)

This document is your master reference for the entire project. It records **every architectural decision, file created, code explained, and interview answer** from absolute scratch to a production-grade system.

---

## Table of Contents
1. [Project Vision & High-Level Architecture](#1-project-vision--high-level-architecture)
2. [Step 0: Directory Structure & Environment Setup](#step-0-directory-structure--environment-setup)
3. [Step 1: Raw Dataset Discovery & Strategy](#step-1-raw-dataset-discovery--strategy)
4. [Step 2: Production Text Cleaning Pipeline (`cleaner.py`)](#step-2-production-text-cleaning-pipeline-cleanerpy)
5. [Step 3: Domain-Aware Semantic Section Chunking (`chunker.py`)](#step-3-domain-aware-semantic-section-chunking-chunkerpy)
6. [Step 4: Vector Embeddings & Vector DB Indexing (`embedder.py` & `store.py`)](#step-4-vector-embeddings--vector-db-indexing)
7. [Step 5: Hybrid Retrieval Engine (BM25 + Dense + RRF)](#step-5-hybrid-retrieval-engine-bm25--dense--rrf)
8. [Step 6: Cross-Encoder Re-Ranking Pipeline](#step-6-cross-encoder-re-ranking-pipeline)
9. [Step 7: Grounded LLM Generation with Citation Attribution](#step-7-grounded-llm-generation-with-citation-attribution)
10. [Step 8: Bridging with Classical Predictive ML (Salary & Placement)](#step-8-bridging-with-classical-predictive-ml)
11. [Step 9: Automated Quantitative Evaluation (Ragas Framework)](#step-9-automated-quantitative-evaluation-ragas-framework)
12. [Step 10: Interactive UI Dashboard & Visual Verification](#step-10-interactive-ui-dashboard--visual-verification)
13. [Master Interview Questions & Answers Cheatsheet](#master-interview-questions--answers-cheatsheet)

---

## 1. Project Vision & High-Level Architecture

### The Problem
Most candidates in AI interviews present a toy "Chat with PDF" app built using default LangChain or LlamaIndex wrappers. These projects fail senior interview screening because:
- They use naive fixed-character chunking (which cuts lists of requirements or skills in half).
- They rely purely on dense vector similarity, which fails on exact keywords (e.g., matching a candidate with `FastAPI` vs `Django`).
- They suffer from context loss (the retrieved chunk has no metadata identifying the company or role).
- They have no quantitative evaluation (no metrics on hallucinations or recall).

### The Solution: CareerLens AI
**CareerLens AI** combines **Classical Predictive ML** (predicting salary and placement readiness from structured student features) with an **Advanced Hybrid RAG System** (performing semantic resume analysis, skill-gap detection, and career trajectory advice grounded in real industry job specs).

$$\text{Raw Documents} \rightarrow \text{Sanitization} \rightarrow \text{Contextual Chunking} \rightarrow \text{Hybrid Indexing (BM25 + ChromaDB)} \rightarrow \text{RRF Fusion} \rightarrow \text{Cross-Encoder Re-ranking} \rightarrow \text{Citation-Grounded LLM} \rightarrow \text{Ragas Evaluation}$$

---

## Step 0: Directory Structure & Environment Setup

### Directory Layout
```
RAG/
├── BUILD_LOG_A_TO_Z.md             <- This master reference guide
├── RESUME_AND_INTERVIEW_GUIDE.md   <- Resume bullets & technical study guide
├── data/
│   ├── raw/                        <- Filtered tech job postings & tech docs
│   ├── resumes/                    <- Benchmark candidate resumes
│   └── processed/                  <- Cleaned, section-split JSONL chunks
├── src/
│   ├── data_pipeline/
│   │   ├── cleaner.py              <- HTML stripping, regex normalization, metadata extraction
│   │   └── chunker.py              <- Domain-aware section chunker with parent header injection
│   ├── vectorstore/
│   │   ├── embedder.py             <- Sentence-Transformers bi-encoder wrapper
│   │   └── store.py                <- ChromaDB persistent collection manager
│   ├── retrieval/
│   │   ├── bm25_retriever.py       <- Sparse keyword retriever (exact tokens)
│   │   ├── dense_retriever.py      <- Dense semantic similarity retriever
│   │   ├── hybrid_retriever.py     <- Reciprocal Rank Fusion (RRF) combiner
│   │   └── reranker.py             <- Cross-Encoder re-ranker for top-K candidates
│   ├── generation/
│   │   ├── prompts.py              <- Grounded system prompts with anti-hallucination constraints
│   │   └── llm_chain.py            <- LLM generation with exact source attribution
│   ├── ml_bridge/
│   │   └── predictor.py            <- Integration with CareerLens LightGBM/XGBoost models
│   └── evaluation/
│       ├── test_dataset.py         <- Golden Q&A test pairs with ground truth
│       └── ragas_eval.py           <- Ragas evaluation metrics runner
├── app/
│   └── streamlit_app.py            <- Interactive portfolio dashboard
└── scripts/
    └── prepare_dataset.py          <- Extraction & preparation script
```

### Core Libraries
- `sentence-transformers`: Local bi-encoders (`all-MiniLM-L6-v2`) and cross-encoders (`ms-marco-MiniLM-L-6-v2`).
- `chromadb`: Production vector database with metadata filtering and persistent local storage.
- `rank-bm25`: Fast BM25 Okapi sparse keyword retrieval.
- `ragas` & `datasets`: Industry-standard RAG evaluation framework.
- `streamlit`: Clean web interface for interactive demos.

---

## Step 1: Raw Dataset Discovery & Strategy

### Real Data Source
Rather than generating synthetic dummy data, we leveraged real hiring datasets from `Placement Platform(CareerLens)`:
- `naukri_raw.csv` (22,000 real job postings): Contains full unstructured job descriptions, requirements, candidate profiles, education requirements, and compensation notes.
- `cleaned_jobs.csv` (33,879 records): Contains clean metadata like `salary_min`, `salary_max`, `standard_title`, and `clean_skills_str`.
- Trained ML models: `salary_model.joblib` and `placement_model.joblib`.

### Target Domain Filtering
For CareerLens AI, we filter for high-demand technology roles:
1. Software Development & Backend (`Python`, `Java`, `FastAPI`, `Go`, `Node.js`)
2. Data Science & Machine Learning (`PyTorch`, `NLP`, `Computer Vision`, `LLMs`, `Pandas`)
3. Data Engineering (`Spark`, `Airflow`, `SQL`, `Snowflake`, `ETL`)
4. Cloud & DevOps (`AWS`, `Docker`, `Kubernetes`, `CI/CD`, `Terraform`)
5. Frontend & Full-Stack (`React`, `TypeScript`, `Next.js`)

---

## Step 2: Production Text Cleaning Pipeline (`cleaner.py`)

Raw job descriptions scraped from job boards contain severe formatting defects:
- Escaped HTML entities (`&amp;`, `&quot;`, `&lt;`)
- HTML tags (`<br>`, `<div>`, `<li>`)
- Unicode replacement garbage (e.g. ``, `\xa0`, `==>`)
- Inconsistent experience strings (`3 - 7 yrs`, `Fresher`, `5+ Yrs`)

### Implementation Details in `src/data_pipeline/cleaner.py`
1. **`TextCleaner.clean_text()`**:
   - Decodes HTML entities and strips HTML tags.
   - Replaces corrupted characters with standard spaces.
   - Normalizes bullet points (`•`, `●`, `▪`, `==>`) into clean Markdown dashes (`- `).
   - Collapses redundant whitespace.
2. **`TextCleaner.parse_experience()`**:
   - Uses regex to parse arbitrary strings into `(min_exp, max_exp)` floats (e.g. `"2 - 5 yrs"` -> `(2.0, 5.0)`).
3. **`TextCleaner.categorize_role()`**:
   - Assigns a standardized tech domain category to power vector database metadata pre-filtering.

---

## Step 3: Domain-Aware Semantic Section Chunking (`chunker.py`)

### The Flaw of Naive Chunking
Standard tutorials use `CharacterTextSplitter(chunk_size=500, chunk_overlap=50)`. 
In career documents, this is catastrophic:
- It splits a bulleted list of required skills across two chunks.
- The retriever finds a chunk that says *"Must have 3 years of experience in AWS, Docker, and Python"*, but the chunk has **zero context** on what job, company, or salary this belongs to! The LLM cannot cite where it came from.

### Our Solution: Hierarchical / Contextual Section Chunker
1. **Structural Splitting**: Detects natural document section headers:
   - `Responsibilities / What You Will Do`
   - `Requirements / Qualifications / Must Have`
   - `Compensation / Benefits`
   - `About the Company`
2. **Context Prefix Injection (Parent Context)**:
   Every single chunk is automatically prepended with a contextual header:
   ```text
   [ROLE: Senior Data Scientist | COMPANY: Acme Corp | DOMAIN: Data Science & AI | EXP: 3-6 yrs | LOCATION: Bangalore | KEY_SKILLS: Python, PyTorch, SQL]
   SECTION: Requirements
   - 3+ years experience developing deep learning models in PyTorch.
   - Proven track record with vector search and RAG architectures.
   ```
3. **Why this matters for interviews**:
   - You solved the **Lost-in-the-Middle** problem.
   - When the vector retriever returns chunk #4, the LLM immediately knows the company, role, experience level, and exact section without needing to load the entire 3-page document.

---

## Step 4: Vector Embeddings & Vector DB Indexing (`embedder.py` & `store.py`)

### Bi-Encoder Architecture (`embedder.py`)
- **Model Selected:** `sentence-transformers/all-MiniLM-L6-v2`
- **Output Dimension:** 384 dimensions
- **Normalization:** Every vector is L2-normalized (`normalize_embeddings=True`).
- **Interview Key Point:** 
  $$\cos(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \vec{u} \cdot \vec{v} \quad \text{when } \|\vec{u}\| = \|\vec{v}\| = 1$$
  Normalizing vectors allows cosine similarity to be computed as an ultra-fast dot product (BLAS matrix multiplication).

### Persistent Vector Database (`store.py`)
- **Technology:** ChromaDB Persistent Client.
- **Index Type:** HNSW (Hierarchical Navigable Small World) graph index with cosine distance space.
- **Metadata Indexing:** Each chunk indexes `doc_id`, `company`, `title`, `category`, `location`, `min_exp`, and `max_exp`.
- **Pre-Filtering:** Supports SQL-like `where={"category": "Data Science & AI"}` to prune candidate search space before vector distance calculation.

---

## Step 5: Hybrid Retrieval Engine (BM25 + Dense + RRF)

### Why Single-Retriever Systems Fail
- **Dense Vector Search Only:** Fails when matching exact acronyms, rare library names, or version identifiers (e.g., `FastAPI`, `Python 3.12`, `K8s`).
- **Sparse BM25 Keyword Search Only:** Fails on semantic intent and synonyms (e.g., cannot match *"cloud container orchestration"* with *"Kubernetes & Docker"*).

### The Solution: Reciprocal Rank Fusion (RRF) in `hybrid_retriever.py`
Instead of attempting complex score normalization between unbounded BM25 scores and cosine similarities, we rank candidates with RRF:
$$RRF(d) = \sum_{m \in \{dense, bm25\}} \frac{1}{k + rank_m(d)} \quad (k = 60)$$
- If a document is ranked #1 in both Dense and BM25, its score is:
  $$\frac{1}{60 + 1} + \frac{1}{60 + 1} = \frac{2}{61} \approx 0.0328$$
- If a document appears in only one list at rank 15, its score is $\frac{1}{75} \approx 0.0133$.
- Top-ranking hits across both modalities get an exponential boost.

---

## Step 6: Cross-Encoder Re-Ranking Pipeline (`reranker.py`)

### Bi-Encoder vs. Cross-Encoder Mechanics
1. **Bi-Encoder (Retriever Stage):**
   - Compares vectors independently: $\vec{q} = f(Query)$ and $\vec{d} = f(Doc)$.
   - Extremely fast ($O(1)$ lookup via HNSW), but misses deep token-to-token semantic interactions.
2. **Cross-Encoder (Re-ranking Stage):**
   - Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
   - Concatenates $[CLS] + Query + [SEP] + Document + [SEP]$ into a single transformer.
   - Computes full cross-attention across every word token simultaneously.
   - Much more accurate, but slower ($O(N)$ transformer forward passes).
3. **The 2-Stage Funnel:**
   $$\text{4,924 Chunks} \xrightarrow[\text{Fast Hybrid Filter}]{\text{Top 20}} \text{20 Candidates} \xrightarrow[\text{Cross-Encoder Attention}]{\text{Top 4}} \text{Top 4 High-Relevance Chunks}$$

---

## Step 7: Grounded LLM Generation with Citation Attribution (`generation/`)

### Strict Anti-Hallucination Prompt Engineering
- **Negative Constraints:** If compensation or specific tools are absent from retrieved context, the prompt explicitly instructs: `"State 'Market data not specified in retrieved records' rather than extrapolating."`
- **Citation Anchors:** Every sentence making a skill claim must append `[Doc: <Company> - <Role> (ID: <chunk_id>)]`.
- **Multi-Provider Support:** Supports OpenAI (GPT-4o), Groq (Llama-3), Gemini, Ollama, and an offline deterministic synthesizer for 100% test reliability.

---

## Step 8: Bridging with Classical Predictive ML (`ml_bridge/`)

Unlike generic chatbots, CareerLens AI unifies **Predictive ML** with **Generative AI**:
1. Candidate metadata (Title, Experience, Skills, Location, CGPA) feeds into pre-trained `HistGradientBoostingRegressor` and `HistGradientBoostingClassifier` models.
2. Outputs:
   - **Predicted Salary (LPA)** based on 33,000+ benchmark jobs.
   - **Placement Readiness Probability (%)**.
3. These ML predictions are displayed alongside the RAG skill-gap analysis, giving candidates both quantitative market value and qualitative roadmaps.

---

## Step 9: Automated Quantitative Evaluation (Ragas Framework)

### The RAG Triad Metrics
1. **Context Precision (Target: > 85%):**
   $$\text{Precision} = \frac{\text{Relevant Chunks in Top-K}}{\text{Total Retrieved Chunks}}$$
   Measures the retriever's ability to prune irrelevant noise.
2. **Context Recall (Target: > 85%):**
   $$\text{Recall} = \frac{\text{Ground-Truth Skills Found in Chunks}}{\text{Total Ground-Truth Skills Required}}$$
   Measures whether the system captured all mandatory requirements.
3. **Faithfulness / Groundedness (Target: > 90%):**
   $$\text{Faithfulness} = \frac{\text{Claims with Valid Grounded Citations}}{\text{Total Factual Claims Generated}}$$
   Guarantees zero hallucinations.
4. **Answer Relevance (Target: > 90%):**
   Evaluates prompt completeness against user intent.

---

## Step 10: Interactive UI Dashboard & Visual Verification (`app/streamlit_app.py`)

The Streamlit app provides 4 dedicated panels:
- **Tab 1: Candidate Career Audit**: Interactive resume analyzer displaying ML salary/placement cards, grounded skill recommendations, and cited source documents.
- **Tab 2: Retrieval Ablation Studio**: Side-by-side comparison of BM25 Keyword Search vs. Dense Vector Search vs. Hybrid + Cross-Encoder Re-Ranking.
- **Tab 3: Automated Benchmark Harness**: Interactive run button that computes live RAG Triad scores across golden test cases.
- **Tab 4: Senior Interview Cheatsheet**: Full answers to all 11 core RAG architectural questions.

---

## Summary of All Created Files

| File | Purpose |
| :--- | :--- |
| `src/data_pipeline/cleaner.py` | Sanitizes HTML, normalizes text, parses experience, categorizes roles |
| `src/data_pipeline/chunker.py` | Hierarchical section chunker injecting contextual parent headers |
| `src/vectorstore/embedder.py` | SentenceTransformers dense bi-encoder with vector normalization |
| `src/vectorstore/store.py` | ChromaDB collection manager with persistent storage and metadata filters |
| `src/retrieval/bm25_retriever.py` | BM25Okapi sparse keyword retriever with tech-aware tokenizer |
| `src/retrieval/dense_retriever.py` | Dense vector retriever |
| `src/retrieval/hybrid_retriever.py`| Reciprocal Rank Fusion (RRF) combining dense & sparse ranks |
| `src/retrieval/reranker.py` | Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) full-attention re-ranker |
| `src/generation/prompts.py` | Grounded system prompts with strict anti-hallucination rules |
| `src/generation/llm_chain.py` | LLM generation supporting OpenAI, Groq, Gemini, and offline synthesizer |
| `src/ml_bridge/predictor.py` | Bridges pre-trained CareerLens salary and placement ML models |
| `src/evaluation/test_dataset.py` | Golden test dataset with ground truth skills and expected answers |
| `src/evaluation/ragas_eval.py` | Automated quantitative evaluation computing the RAG Triad |
| `src/pipeline.py` | Master pipeline orchestrator connecting all modules |
| `app/streamlit_app.py` | Interactive portfolio dashboard for live demos |
| `scripts/prepare_dataset.py` | Data extraction and chunking pipeline |
| `scripts/build_indexes.py` | Index builder for BM25 and ChromaDB |
| `RESUME_AND_INTERVIEW_GUIDE.md` | Copy-paste resume bullets & deep technical study curriculum |
| `BUILD_LOG_A_TO_Z.md` | This complete end-to-end master document |

