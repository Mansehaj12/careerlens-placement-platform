"""
CareerLens AI — Interactive Portfolio & Interview Showcase App
Demonstrates Hybrid RAG (BM25 + Dense), Cross-Encoder Re-Ranking, Classical ML Predictions,
and Automated RAG Evaluation in an intuitive, production-grade interface.
"""

import os
import sys
import json
import streamlit as st
import pandas as pd

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline import CareerLensPipeline
from src.evaluation.test_dataset import GOLDEN_TEST_CASES

st.set_page_config(
    page_title="CareerLens AI — Career Intelligence & RAG Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border: 1px solid #2e3646;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    .citation-box {
        background-color: #161b22;
        border-left: 4px solid #3b82f6;
        padding: 10px 14px;
        margin-top: 8px;
        border-radius: 4px;
        font-size: 0.88rem;
    }
    .badge {
        background-color: #2563eb;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_pipeline():
    """Caches pipeline initialization to avoid reloading models on rerun."""
    return CareerLensPipeline()


def main():
    st.title("🚀 CareerLens AI")
    st.markdown(
        "**AI-Powered Career Intelligence Platform** combining **Classical Predictive ML** (Salary & Placement Models) "
        "with **Advanced Hybrid RAG** (BM25 + Dense Vector Search + Cross-Encoder Re-Ranking + Citations)."
    )
    st.markdown(
        '<span class="badge">Hybrid Search (BM25 + Dense)</span>'
        '<span class="badge">Reciprocal Rank Fusion (RRF)</span>'
        '<span class="badge">Cross-Encoder Re-Ranking</span>'
        '<span class="badge">Strict Anti-Hallucination Guardrails</span>'
        '<span class="badge">Ragas Evaluated</span>',
        unsafe_allow_html=True
    )
    st.write("")

    pipeline = load_pipeline()

    # Sidebar
    st.sidebar.header("⚙️ Pipeline Configuration")
    target_role = st.sidebar.selectbox(
        "Target Role",
        ["Data Scientist", "Software Engineer", "Machine Learning Engineer", "DevOps Engineer", "Data Analyst", "Full Stack Developer"]
    )
    experience_level = st.sidebar.selectbox(
        "Experience Tier",
        ["Entry-level (0-2 yrs)", "Mid-level (3-5 yrs)", "Senior (5+ yrs)"]
    )
    location = st.sidebar.selectbox("Preferred Location", ["Bangalore", "Hyderabad", "Pune", "Mumbai", "Delhi NCR", "Remote"])
    remote_status = st.sidebar.selectbox("Work Mode", ["Hybrid", "Remote", "On-site"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎓 Candidate Academic Profile (For ML)")
    cgpa = st.sidebar.slider("CGPA", 5.0, 10.0, 8.4, 0.1)
    internships = st.sidebar.slider("Internships Completed", 0, 4, 1)
    projects_cnt = st.sidebar.slider("Technical Projects", 0, 8, 3)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔬 Retrieval & Reranker Controls")
    use_reranker = st.sidebar.checkbox("Enable Cross-Encoder Re-Ranking (ms-marco)", value=True)
    top_k = st.sidebar.slider("Final Context Chunks (Top-K)", 2, 8, 4)

    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Candidate Career Audit",
        "🔬 Retrieval Comparison (Ablation)",
        "🧪 Automated Ragas Benchmark",
        "📚 Interview Q&A & Architecture"
    ])

    with tab1:
        st.subheader("1. Candidate Resume / Profile Input")
        default_resume = (
            "Name: Aarav Sharma\n"
            "Target Role: Machine Learning Engineer / AI Developer\n"
            "Experience: 0.5 years\n"
            "Education: B.Tech Computer Science (8.4 CGPA)\n"
            "Core Skills: Python, PyTorch, Scikit-Learn, Pandas, NumPy, SQL, Git, Flask\n"
            "Projects:\n"
            "- CareerLens: Placement readiness & salary predictor with LightGBM and scikit-learn\n"
            "- Real-Time Computer Vision: Object detection with YOLOv8 & OpenCV\n"
            "- NLP Sentiment Classifier: Fine-tuned DistilBERT on customer reviews\n"
            "Certifications: Deep Learning Specialization (Coursera), AWS Cloud Practitioner"
        )
        candidate_profile = st.text_area("Paste Candidate Profile or Resume Text:", value=default_resume, height=180)

        if st.button("🚀 Run Career Intelligence Audit", type="primary"):
            with st.spinner("Executing Classical ML inference + Hybrid RAG retrieval + Re-ranking..."):
                results = pipeline.run_full_audit(
                    candidate_profile=candidate_profile,
                    target_role=target_role,
                    experience_level=experience_level,
                    location=location,
                    remote=remote_status,
                    cgpa=cgpa,
                    internships=internships,
                    projects=projects_cnt,
                    use_reranker=use_reranker,
                    top_k=top_k
                )

            # Display Key Metrics
            ml_pred = results["ml_predictions"]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Predicted Salary (ML)", f"₹{ml_pred['predicted_salary_lpa']} LPA", help="Predicted by trained HistGradientBoosting Regressor")
            with col2:
                st.metric("🎯 Placement Probability", f"{ml_pred['placement_probability_pct']}%", delta=ml_pred['placement_tier'])
            with col3:
                st.metric("📑 Retrieved JDs", f"{results['raw_candidates_count']} Candidates", help="Retrieved via Dense + BM25 Hybrid Search")
            with col4:
                st.metric("⚡ Re-ranked Context", f"{len(results['retrieved_chunks'])} Chunks", delta="Filtered with Cross-Encoder")

            st.markdown("---")

            # Two-column layout: Report vs Retrieved Ground-Truth Documents
            col_report, col_sources = st.columns([6, 4])

            with col_report:
                st.subheader("📋 Citation-Grounded Career Report")
                st.markdown(results["report"])
                st.caption(f"Generated via **{results['provider']}** using model: `{results['model']}`")

            with col_sources:
                st.subheader("🔍 Ground-Truth Retrieved Sources")
                st.info("The LLM is constrained to base its recommendations strictly on these retrieved chunks:")
                for i, chunk in enumerate(results["retrieved_chunks"], 1):
                    meta = chunk.get("metadata", {})
                    rerank_score = chunk.get("rerank_score")
                    prior_score = chunk.get("prior_score") or chunk.get("score")
                    score_info = f"Re-rank Score: {rerank_score} | Initial RRF: {prior_score}" if rerank_score else f"Score: {prior_score}"

                    with st.expander(f"Doc {i}: {meta.get('company', 'Company')} — {meta.get('title', 'Role')}"):
                        st.caption(f"**Chunk ID:** `{chunk.get('chunk_id')}` | **Domain:** `{meta.get('category')}`")
                        st.caption(f"**Scores:** `{score_info}`")
                        st.text(chunk.get("text", "")[:350] + "...")

    with tab2:
        st.subheader("🔬 Retrieval Ablation: Why Hybrid + Re-ranking Wins")
        st.markdown(
            "Answering the classic interview question: *'Why not just use cosine similarity?'*\n\n"
            "This interactive test executes the same query across all 3 retrieval stages simultaneously:"
        )

        test_q = st.text_input("Test Query for Ablation:", value="FastAPI microservices Docker Kubernetes backend developer")

        if st.button("Run Retrieval Comparison"):
            with st.spinner("Querying BM25, Dense Vector, and Hybrid + Re-ranker..."):
                bm25_hits = pipeline.bm25_retriever.search(test_q, top_k=3) if pipeline.bm25_retriever else []
                dense_hits = pipeline.dense_retriever.search(test_q, top_k=3)
                hybrid_hits = pipeline.hybrid_retriever.search(test_q, top_k=6) if pipeline.hybrid_retriever else []
                reranked_hits = pipeline.reranker.rerank(test_q, hybrid_hits, top_k=3) if pipeline.reranker else []

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.markdown("#### 1. Sparse BM25 (Keywords)")
                st.caption("Matches exact word frequencies. Misses synonyms.")
                for h in bm25_hits:
                    st.write(f"- **{h['metadata'].get('title')}** at *{h['metadata'].get('company')}* (Score: {h['score']})")

            with col_b:
                st.markdown("#### 2. Dense Vector (Cosine)")
                st.caption("Matches semantic concept. Struggles with rare acronyms.")
                for h in dense_hits:
                    st.write(f"- **{h['metadata'].get('title')}** at *{h['metadata'].get('company')}* (Cosine: {h['score']})")

            with col_c:
                st.markdown("#### 3. Hybrid + Re-ranker (Ours)")
                st.caption("Fuses both via RRF and runs full cross-attention!")
                for h in reranked_hits:
                    st.write(f"- **{h['metadata'].get('title')}** at *{h['metadata'].get('company')}* (Logit: {h.get('rerank_score')})")

    with tab3:
        st.subheader("🧪 Automated Quantitative Evaluation (Ragas Framework)")
        st.markdown(
            "Interviewers want objective proof that your RAG pipeline doesn't hallucinate. "
            "We benchmark our pipeline against the **RAG Triad** across standardized golden test cases."
        )

        if st.button("▶️ Run Automated Evaluation Benchmark"):
            with st.spinner("Evaluating Faithfulness, Context Recall, Precision, and Answer Relevance..."):
                eval_metrics = pipeline.run_evaluation_suite()

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Context Precision", f"{eval_metrics['mean_context_precision'] * 100:.1f}%", help="Noisy chunk rejection rate")
            col_m2.metric("Context Recall", f"{eval_metrics['mean_context_recall'] * 100:.1f}%", help="Required skill capture rate")
            col_m3.metric("Faithfulness", f"{eval_metrics['mean_faithfulness'] * 100:.1f}%", help="Grounded claim validation")
            col_m4.metric("Answer Relevance", f"{eval_metrics['mean_answer_relevance'] * 100:.1f}%", help="Prompt alignment")

            st.write("")
            st.markdown("### Test Suite Breakdown")
            df_eval = pd.DataFrame(eval_metrics["test_breakdown"])
            st.dataframe(df_eval, use_container_width=True)

    with tab4:
        st.subheader("📚 Interview Master Cheatsheet: The 11 Core Questions")
        st.markdown(
            "Here are the exact answers to explain this architecture to senior interviewers:"
        )

        qa_pairs = [
            ("Why did you choose RAG over Fine-Tuning?",
             "Fine-tuning changes model style/syntax, but suffers from factual hallucinations and cannot reliably memorize dynamic market data. Job market specs and salary percentiles change frequently; RAG allows instant zero-cost knowledge base updates with guaranteed source attribution."),
            ("Why embeddings and vector search?",
             "Lexical search fails when candidates use synonyms (e.g. 'Golang' vs 'Go', or 'Kubernetes orchestration' vs 'Container management'). Dense embeddings map semantic meaning into high-dimensional space so resumes and job descriptions match conceptually."),
            ("Why ChromaDB over FAISS or pgvector?",
             "ChromaDB provides lightweight local persistence with native metadata filtering. In an enterprise setting with relational user accounts, we transition to pgvector to keep relational student records and vector embeddings in a single ACID-compliant PostgreSQL database."),
            ("How did you chunk documents?",
             "Resumes and job descriptions have structural boundaries. Naive fixed-character chunking breaks bulleted qualifications in half. We built a hierarchical section chunker that splits on headers (Responsibilities, Requirements, Compensation) and prepends parent metadata (Role, Company, Experience) to every single chunk."),
            ("How did you reduce hallucinations?",
             "Through 3 tiers: (1) Cross-encoder filtering to prune irrelevant context, (2) Strict negative prompt instructions ('If not in context, state unmentioned'), and (3) Mandatory citation anchors [Doc: Company - Role (ID)]."),
            ("What happens if retrieval returns irrelevant documents?",
             "We implemented similarity score thresholds. Chunks falling below the cross-encoder cutoff are discarded. If zero relevant documents survive, the system triggers graceful fallback instead of guessing."),
            ("How did you evaluate your RAG system?",
             "Using the Ragas RAG Triad: Context Recall (did we fetch required skills?), Context Precision (did we filter out noise?), and Faithfulness (are output claims strictly grounded in retrieved docs?)."),
            ("How would you scale this to 100,000 documents?",
             "Transition from flat indexing to HNSW index for sub-millisecond approximate nearest neighbor search, apply metadata pre-filtering by role category, and implement asynchronous document processing with Celery/Redis.")
        ]

        for q, a in qa_pairs:
            with st.expander(f"❓ {q}"):
                st.write(a)


if __name__ == "__main__":
    main()
