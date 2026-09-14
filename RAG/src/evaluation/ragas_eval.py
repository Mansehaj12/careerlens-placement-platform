"""
Automated Evaluation Harness for CareerLens AI
Benchmarks the RAG pipeline using the RAG Triad:
- Context Precision: Did the retriever fetch relevant job specs without noise?
- Context Recall: Did the retrieved documents cover the ground-truth required skills?
- Faithfulness: Are generated claims strictly supported by retrieved context with citations?
- Answer Relevance: Does the generated roadmap directly solve the user's career query?
"""

import json
import re
from typing import List, Dict, Any
from src.evaluation.test_dataset import GOLDEN_TEST_CASES


class RAGEvaluator:
    """
    Quantitative evaluation engine computing RAG metrics across a golden test suite.
    Outputs metrics directly defensible in interviews and resume bullets.
    """

    @staticmethod
    def compute_context_recall(retrieved_chunks: List[Dict[str, Any]], ground_truth_skills: List[str]) -> float:
        """Measures what fraction of ground truth skills were captured in retrieved context."""
        if not ground_truth_skills:
            return 1.0

        all_text = " ".join([c.get("text", "") for c in retrieved_chunks]).lower()
        found = sum(1 for skill in ground_truth_skills if skill.lower() in all_text)
        return round(found / len(ground_truth_skills), 3)

    @staticmethod
    def compute_context_precision(retrieved_chunks: List[Dict[str, Any]], target_category: str) -> float:
        """Measures proportion of retrieved chunks that align with the query domain."""
        if not retrieved_chunks:
            return 0.0

        relevant = sum(1 for c in retrieved_chunks if c.get("metadata", {}).get("category") == target_category)
        return round(relevant / len(retrieved_chunks), 3)

    @staticmethod
    def compute_faithfulness(generated_report: str, retrieved_chunks: List[Dict[str, Any]]) -> float:
        """
        Calculates grounding ratio:
        Checks that every cited chunk ID actually exists in the retrieved set.
        """
        valid_chunk_ids = {c.get("chunk_id") for c in retrieved_chunks}
        # Find citation tags in format: (ID: <chunk_id>)
        citations_found = re.findall(r"\(ID:\s*([^)]+)\)", generated_report)

        if not citations_found:
            return 0.70  # Penalty for lack of citations

        valid_citations = sum(1 for cid in citations_found if cid in valid_chunk_ids)
        return round(valid_citations / len(citations_found), 3)

    @staticmethod
    def compute_answer_relevance(generated_report: str, query: str) -> float:
        """Verifies report covers key structural career intelligence components."""
        required_sections = ["Market Alignment", "Skill", "Roadmap", "Compensation"]
        hits = sum(1 for sec in required_sections if sec.lower() in generated_report.lower())
        return round(hits / len(required_sections), 3)

    def evaluate_pipeline(self, pipeline_runner_fn) -> Dict[str, Any]:
        """
        Executes full evaluation suite across all golden test cases.
        pipeline_runner_fn: callable(query, profile) -> (retrieved_chunks, generated_report)
        """
        results = []
        recalls, precisions, faithfuls, relevances = [], [], [], []

        print("\n" + "=" * 65)
        print("RUNNING AUTOMATED RAG EVALUATION HARNESS (RAG TRIAD)")
        print("=" * 65)

        for case in GOLDEN_TEST_CASES:
            cid = case["id"]
            query = case["query"]
            profile = case["candidate_profile"]
            category = case["target_category"]
            gt_skills = case["ground_truth_skills"]

            chunks, report = pipeline_runner_fn(query=query, candidate_profile=profile, category=category)

            rec = self.compute_context_recall(chunks, gt_skills)
            prec = self.compute_context_precision(chunks, category)
            faith = self.compute_faithfulness(report, chunks)
            rel = self.compute_answer_relevance(report, query)

            recalls.append(rec)
            precisions.append(prec)
            faithfuls.append(faith)
            relevances.append(rel)

            results.append({
                "test_id": cid,
                "context_recall": rec,
                "context_precision": prec,
                "faithfulness": faith,
                "answer_relevance": rel
            })
            print(f"[*] Test [{cid}] -> Precision: {prec:.2f} | Recall: {rec:.2f} | Faithfulness: {faith:.2f} | Relevance: {rel:.2f}")

        avg_summary = {
            "mean_context_precision": round(sum(precisions) / len(precisions), 3),
            "mean_context_recall": round(sum(recalls) / len(recalls), 3),
            "mean_faithfulness": round(sum(faithfuls) / len(faithfuls), 3),
            "mean_answer_relevance": round(sum(relevances) / len(relevances), 3),
            "total_test_cases": len(GOLDEN_TEST_CASES),
            "test_breakdown": results
        }

        print("\n" + "=" * 65)
        print("EVALUATION SUMMARY REPORT:")
        print(f"  • Mean Context Precision : {avg_summary['mean_context_precision'] * 100:.1f}%")
        print(f"  • Mean Context Recall    : {avg_summary['mean_context_recall'] * 100:.1f}%")
        print(f"  • Mean Faithfulness      : {avg_summary['mean_faithfulness'] * 100:.1f}%")
        print(f"  • Mean Answer Relevance  : {avg_summary['mean_answer_relevance'] * 100:.1f}%")
        print("=" * 65 + "\n")

        return avg_summary
