"""
Unified CareerLens AI Master Pipeline Orchestrator
Integrates:
1. Candidate Profile Parsing
2. Classical ML Salary & Placement Prediction
3. Hybrid Retrieval (BM25 + Dense) with RRF
4. Cross-Encoder Re-Ranking
5. Citation-Grounded LLM Generation
6. Evaluation Harness
"""

import os
import json
from typing import Dict, Any, List, Optional

from src.vectorstore.embedder import DocumentEmbedder
from src.vectorstore.store import CareerVectorStore
from src.retrieval.bm25_retriever import CareerBM25Retriever
from src.retrieval.dense_retriever import CareerDenseRetriever
from src.retrieval.hybrid_retriever import CareerHybridRetriever
from src.retrieval.reranker import CareerCrossEncoderReranker
from src.generation.llm_chain import CareerLensGenerator
from src.ml_bridge.predictor import CareerMLBridge
from src.evaluation.ragas_eval import RAGEvaluator


class CareerLensPipeline:
    """
    The end-to-end CareerLens AI Pipeline.
    Combines classical predictive ML with advanced RAG.
    """

    def __init__(self, bm25_path: str = r"data\bm25_index.pkl", chroma_dir: str = r"data\chroma_db"):
        print("[*] Initializing CareerLens AI System Components...")
        self.embedder = DocumentEmbedder()
        self.store = CareerVectorStore(persist_dir=chroma_dir)
        self.dense_retriever = CareerDenseRetriever(self.embedder, self.store)

        # Load BM25 index if exists
        self.bm25_retriever = None
        if os.path.exists(bm25_path):
            self.bm25_retriever = CareerBM25Retriever.load(bm25_path)
            self.hybrid_retriever = CareerHybridRetriever(self.dense_retriever, self.bm25_retriever)
        else:
            self.hybrid_retriever = None

        self.reranker = CareerCrossEncoderReranker()
        self.generator = CareerLensGenerator()
        self.ml_bridge = CareerMLBridge()
        self.evaluator = RAGEvaluator()
        print("[+] CareerLens AI components initialized.")

    def run_full_audit(
        self,
        candidate_profile: str,
        target_role: str = "Data Scientist",
        experience_level: str = "Entry-level (0-2 yrs)",
        location: str = "Bangalore",
        remote: str = "Hybrid",
        cgpa: float = 8.2,
        internships: int = 1,
        projects: int = 3,
        use_reranker: bool = True,
        top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Executes end-to-end CareerLens AI audit:
        1. Predicts salary & placement odds using Classical ML
        2. Retrieves relevant market benchmarks via Hybrid Search (BM25 + Dense)
        3. Re-ranks top candidates with Cross-Encoder
        4. Synthesizes citation-grounded career intelligence report
        """
        # Step 1: Classical ML Prediction
        ml_predictions = self.ml_bridge.predict_salary_and_placement(
            standard_title=target_role,
            experience_level=experience_level,
            location=location,
            remote=remote,
            cgpa=cgpa,
            internships=internships,
            projects=projects
        )

        # Step 2: Retrieval
        query = f"Target Role: {target_role}. Requirements and skills for {experience_level}. Profile: {candidate_profile[:250]}"

        if self.hybrid_retriever:
            retrieved = self.hybrid_retriever.search(query, top_k=15, candidate_pool_size=20)
        else:
            retrieved = self.dense_retriever.search(query, top_k=15)

        # Step 3: Re-ranking
        if use_reranker and self.reranker:
            final_chunks = self.reranker.rerank(query, retrieved, top_k=top_k)
        else:
            final_chunks = retrieved[:top_k]

        # Step 4: Grounded LLM Generation
        gen_output = self.generator.generate_report(candidate_profile, final_chunks)

        return {
            "ml_predictions": ml_predictions,
            "retrieved_chunks": final_chunks,
            "raw_candidates_count": len(retrieved),
            "report": gen_output["report"],
            "provider": gen_output["provider"],
            "model": gen_output["model"]
        }

    def run_evaluation_suite(self) -> Dict[str, Any]:
        """Runs the automated RAG evaluation benchmark."""
        def runner(query: str, candidate_profile: str, category: str):
            where_filter = {"category": category} if category else None
            chunks = self.dense_retriever.search(query, top_k=4, where_filter=where_filter)
            if self.reranker:
                chunks = self.reranker.rerank(query, chunks, top_k=4)
            gen = self.generator.generate_report(candidate_profile, chunks)
            return chunks, gen["report"]

        return self.evaluator.evaluate_pipeline(runner)
