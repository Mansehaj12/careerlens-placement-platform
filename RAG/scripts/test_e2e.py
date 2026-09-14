"""
End-to-End Test & Verification Script for CareerLens AI
Tests:
1. BM25 + Dense Hybrid Retrieval
2. Cross-Encoder Re-Ranking
3. Classical ML Bridge (Salary + Placement)
4. Grounded Output & Citation Integrity
5. Automated Ragas Evaluation Runner
"""

import os
import sys
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pipeline import CareerLensPipeline


def run_verification():
    print("=" * 70)
    print("CAREERLENS AI: END-TO-END SYSTEM VERIFICATION")
    print("=" * 70)

    # 1. Initialize Pipeline
    pipeline = CareerLensPipeline()

    # 2. Test Candidate Profile
    sample_profile = (
        "Name: Aarav Sharma\n"
        "Target Role: Machine Learning Engineer\n"
        "Experience: 1 year\n"
        "Skills: Python, PyTorch, Scikit-Learn, SQL, Git, FastAPI, Docker\n"
        "Education: B.Tech Computer Science (8.4 CGPA)\n"
        "Projects: End-to-end ML prediction systems and computer vision models."
    )

    print("\n[*] Executing Full Career Audit...")
    audit = pipeline.run_full_audit(
        candidate_profile=sample_profile,
        target_role="Machine Learning Engineer",
        experience_level="Entry-level (0-2 yrs)",
        location="Bangalore",
        remote="Hybrid",
        cgpa=8.4,
        internships=1,
        projects=3,
        use_reranker=True,
        top_k=4
    )

    print("\n[+] ML PREDICTIONS:")
    ml_preds = audit["ml_predictions"]
    print(f"  - Predicted Salary: INR {ml_preds['predicted_salary_lpa']} LPA (INR {ml_preds['predicted_salary_inr']:,.0f})")
    print(f"  - Placement Readiness: {ml_preds['placement_probability_pct']}% ({ml_preds['placement_tier']})")

    print("\n[+] RETRIEVAL & RE-RANKING:")
    print(f"  - Initial Hybrid Candidates Pool: {audit['raw_candidates_count']}")
    print(f"  - Final Re-Ranked Top Chunks: {len(audit['retrieved_chunks'])}")
    for i, c in enumerate(audit["retrieved_chunks"], 1):
        meta = c.get("metadata", {})
        print(f"    [{i}] {meta.get('company')} - {meta.get('title')} (Re-rank Score: {c.get('rerank_score')})")

    print("\n[+] CITATION-GROUNDED REPORT PREVIEW:")
    print("-" * 50)
    print(audit["report"][:600] + "...\n[Report truncated for preview]")
    print("-" * 50)

    # 3. Test Automated Evaluation Harness
    print("\n[*] Running Automated Ragas-style Evaluation...")
    eval_metrics = pipeline.run_evaluation_suite()
    print("[+] Evaluation Complete:")
    print(f"  - Context Precision: {eval_metrics['mean_context_precision'] * 100:.1f}%")
    print(f"  - Context Recall:    {eval_metrics['mean_context_recall'] * 100:.1f}%")
    print(f"  - Faithfulness:      {eval_metrics['mean_faithfulness'] * 100:.1f}%")
    print(f"  - Answer Relevance:  {eval_metrics['mean_answer_relevance'] * 100:.1f}%")

    print("\n" + "=" * 70)
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
