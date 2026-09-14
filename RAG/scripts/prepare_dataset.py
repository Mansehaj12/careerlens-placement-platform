"""
Data Preparation & Ingestion Pipeline for CareerLens AI
Extracts real tech job postings from Naukri dataset, cleans text, extracts metadata,
generates technical benchmark documents and sample resumes, then chunks all documents.
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_pipeline.cleaner import TextCleaner
from src.data_pipeline.chunker import CareerDocChunker

NAUKRI_CSV_PATH = r"c:\Users\HP\OneDrive\Desktop\Codes\Projects All\Placement Platform(CareerLens)\Datasets\naukri_raw.csv"
CLEANED_CSV_PATH = r"c:\Users\HP\OneDrive\Desktop\Codes\Projects All\Placement Platform(CareerLens)\Datasets\cleaned_jobs.csv"

OUTPUT_RAW_JOBS = r"data\raw\tech_jobs.json"
OUTPUT_TECH_DOCS = r"data\raw\tech_competency_docs.json"
OUTPUT_PROCESSED_CHUNKS = r"data\processed\job_chunks.jsonl"
RESUMES_DIR = r"data\resumes"


def extract_tech_jobs(limit: int = 1200) -> list:
    print(f"[*] Reading raw job postings from: {NAUKRI_CSV_PATH}")
    df = pd.read_csv(NAUKRI_CSV_PATH)
    print(f"[*] Total rows in raw dataset: {len(df)}")

    # Drop rows without job description
    df = df.dropna(subset=["jobdescription", "jobtitle"]).copy()

    extracted = []
    seen_titles = set()

    for idx, row in df.iterrows():
        title = str(row.get("jobtitle", "")).strip()
        skills = str(row.get("skills", "")).strip()
        company = str(row.get("company", "Confidential")).strip()
        raw_desc = str(row.get("jobdescription", "")).strip()
        location = str(row.get("joblocation_address", "Remote / India")).strip()
        exp_raw = str(row.get("experience", "")).strip()
        payrate = str(row.get("payrate", "Not Disclosed")).strip()

        if len(raw_desc) < 120:
            continue

        # Categorize
        category = TextCleaner.categorize_role(title, skills)
        if category == "General Tech":
            # Check if description mentions strong tech keywords
            desc_lower = raw_desc.lower()
            if any(k in desc_lower for k in ["python", "java", "sql", "aws", "machine learning", "react", "c++"]):
                category = "Backend & Software Engineering"
            else:
                continue

        # Clean text
        clean_desc = TextCleaner.clean_text(raw_desc)
        min_exp, max_exp = TextCleaner.parse_experience(exp_raw)

        # Avoid exact duplicate descriptions
        dedup_key = (company.lower(), title.lower()[:30])
        if dedup_key in seen_titles:
            continue
        seen_titles.add(dedup_key)

        job_id = f"job_{row.get('uniq_id', str(idx))}"

        doc = {
            "id": job_id,
            "title": title,
            "company": company,
            "category": category,
            "skills": skills,
            "location": location,
            "min_exp": min_exp,
            "max_exp": max_exp,
            "salary": payrate,
            "description": clean_desc
        }
        extracted.append(doc)

        if len(extracted) >= limit:
            break

    print(f"[+] Successfully extracted {len(extracted)} structured tech job postings across domains.")
    return extracted


def create_technical_competency_docs() -> list:
    """Creates curated technical competency documents used for skill-gap & learning recommendations."""
    docs = [
        {
            "id": "doc_tech_python",
            "title": "Python Core & Advanced Engineering Standards",
            "company": "Engineering Competency Framework",
            "category": "Backend & Software Engineering",
            "skills": "Python, GIL, Generators, Asyncio, Memory Management, Typing",
            "location": "Global",
            "min_exp": 0.0,
            "max_exp": 8.0,
            "salary": "Standard",
            "description": (
                "Python Engineering Competency Overview:\n"
                "Requirements & Core Concepts:\n"
                "- Deep understanding of Python internals: Global Interpreter Lock (GIL), garbage collection (reference counting + cyclic GC), and memory management.\n"
                "- Asynchronous programming using asyncio, event loops, coroutines, and task management.\n"
                "- Metaprogramming with decorators, dunder methods, generators, context managers, and descriptors.\n"
                "- Clean architecture: Type hinting (PEP 484), dataclasses, Pydantic validation, and modular packaging.\n"
                "Interview Expectations:\n"
                "- Candidates must explain time complexity of dictionary lookups (hash collisions and open addressing).\n"
                "- Ability to profile code with cProfile, memory_profiler, and optimize bottlenecks with vectorization or multiprocessing."
            )
        },
        {
            "id": "doc_tech_rag_llm",
            "title": "Production LLM & RAG Systems Architecture",
            "company": "AI Engineering Framework",
            "category": "Data Science & AI",
            "skills": "RAG, Vector DB, Chroma, FAISS, Embeddings, Cross-Encoders, Ragas, LangChain",
            "location": "Global",
            "min_exp": 1.0,
            "max_exp": 6.0,
            "salary": "High Tier",
            "description": (
                "Production RAG & Generative AI Standards:\n"
                "Core Architecture:\n"
                "- Dense vector retrieval using bi-encoders (all-MiniLM-L6-v2, BGE) combined with sparse keyword retrieval (BM25) via Reciprocal Rank Fusion (RRF).\n"
                "- Cross-Encoder re-ranking to calibrate semantic relevance and filter out noisy context before passing to LLM context windows.\n"
                "- Hierarchical section-aware chunking with parent-document metadata propagation to eliminate context fragmentation.\n"
                "Evaluation & Guardrails:\n"
                "- Quantitative evaluation using the RAG Triad: Context Precision, Context Recall, and Faithfulness (groundedness).\n"
                "- Hallucination mitigation through strict negative system prompts, source citation constraints, and similarity score cutoffs."
            )
        },
        {
            "id": "doc_tech_cloud_devops",
            "title": "Cloud Infrastructure, Containers & Kubernetes Standards",
            "company": "Cloud Engineering Framework",
            "category": "DevOps & Cloud",
            "skills": "Docker, Kubernetes, AWS, Terraform, CI/CD, Helm, Observability",
            "location": "Global",
            "min_exp": 1.0,
            "max_exp": 7.0,
            "salary": "High Tier",
            "description": (
                "Cloud & Container Orchestration Standards:\n"
                "Core Architecture & Requirements:\n"
                "- Docker containerization: Multi-stage builds, minimal base images (Alpine/Distroless), non-root users, and layer caching.\n"
                "- Kubernetes orchestration: Pod lifecycle, Deployments, ReplicaSets, Services (ClusterIP/NodePort/Ingress), ConfigMaps, Secrets, and Horizontal Pod Autoscaling (HPA).\n"
                "- Infrastructure as Code (IaC) using Terraform for AWS resources (VPC, EKS, RDS, S3, IAM roles).\n"
                "- CI/CD automation with GitHub Actions / GitLab CI, including automated linting, unit testing, image vulnerability scanning (Trivy), and deployment pipelines."
            )
        },
        {
            "id": "doc_tech_data_engineering",
            "title": "Data Engineering, Streaming & Warehouse Standards",
            "company": "Data Infrastructure Framework",
            "category": "Data Engineering",
            "skills": "SQL, Apache Spark, PySpark, Airflow, Snowflake, Kafka, Data Modeling",
            "location": "Global",
            "min_exp": 1.0,
            "max_exp": 6.0,
            "salary": "High Tier",
            "description": (
                "Data Engineering Competency Standards:\n"
                "Core Architecture & Requirements:\n"
                "- Distributed data processing with Apache Spark (PySpark): RDDs vs DataFrames, catalyst optimizer, partition tuning, shuffle minimization, and broadcast joins.\n"
                "- Data modeling: Star schema, snowflake schema, slowly changing dimensions (SCD Type 1 & 2), and columnar storage (Parquet/ORC).\n"
                "- Workflow orchestration using Apache Airflow: DAG architecture, operators, sensors, backfilling, and XCom best practices.\n"
                "- Advanced SQL: Window functions (ROW_NUMBER, RANK, DENSE_RANK), CTEs, indexing strategies (B-Tree, Hash), and query execution plan analysis (EXPLAIN ANALYZE)."
            )
        }
    ]
    return docs


def create_sample_resumes():
    """Generates realistic test candidate resumes in data/resumes/ to test matching and evaluation."""
    resumes = {
        "candidate_fresher_aiml.json": {
            "name": "Aarav Sharma",
            "target_role": "Machine Learning Engineer / AI Developer",
            "experience_years": 0.5,
            "skills": ["Python", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "SQL", "Git", "Flask"],
            "education": "B.Tech in Computer Science (8.4 CGPA)",
            "projects": [
                "CareerLens: Placement Readiness & Salary Predictor using LightGBM and Random Forest",
                "Computer Vision: Real-time Object Detection with YOLOv8 and OpenCV",
                "NLP: Sentiment Analysis on Product Reviews using BERT and Hugging Face"
            ],
            "certifications": ["Deep Learning Specialization (Coursera)", "AWS Certified Cloud Practitioner"]
        },
        "candidate_mid_backend.json": {
            "name": "Priya Patel",
            "target_role": "Senior Backend Software Engineer",
            "experience_years": 3.5,
            "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS", "Git"],
            "education": "B.E. in Information Technology",
            "projects": [
                "Scalable Microservices Backend: Built high-throughput API gateway processing 5,000 req/sec with FastAPI & Redis caching",
                "Database Migration: Optimized slow PostgreSQL queries using indexing and partitioning, reducing P99 latency by 60%",
                "Event-Driven Pipeline: Implemented asynchronous messaging with RabbitMQ and Celery"
            ],
            "certifications": ["AWS Certified Solutions Architect Associate"]
        },
        "candidate_data_analyst.json": {
            "name": "Rohan Gupta",
            "target_role": "Data Analyst / BI Specialist",
            "experience_years": 1.5,
            "skills": ["SQL", "Power BI", "Tableau", "Excel", "Python", "Pandas", "Data Cleaning", "Storytelling"],
            "education": "B.Sc in Statistics",
            "projects": [
                "E-Commerce Executive Dashboard: Designed automated Power BI dashboard tracking revenue, churn, and customer lifetime value",
                "Supply Chain Analytics: Optimized inventory turnover by writing complex SQL window queries"
            ],
            "certifications": ["Microsoft Certified: Power BI Data Analyst Associate"]
        }
    }

    for filename, data in resumes.items():
        filepath = os.path.join(RESUMES_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    print(f"[+] Created {len(resumes)} benchmark candidate resumes in {RESUMES_DIR}")


def main():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs(RESUMES_DIR, exist_ok=True)

    # 1. Extract Tech Jobs
    jobs = extract_tech_jobs(limit=1200)
    with open(OUTPUT_RAW_JOBS, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)
    print(f"[+] Saved raw tech jobs to {OUTPUT_RAW_JOBS}")

    # 2. Add Tech Competency Docs
    competency_docs = create_technical_competency_docs()
    with open(OUTPUT_TECH_DOCS, "w", encoding="utf-8") as f:
        json.dump(competency_docs, f, indent=2)
    print(f"[+] Saved tech competency documents to {OUTPUT_TECH_DOCS}")

    # 3. Create Sample Resumes
    create_sample_resumes()

    # 4. Chunk All Documents using Domain-Aware Chunker
    print("[*] Chunking documents with CareerDocChunker...")
    chunker = CareerDocChunker(max_chunk_chars=1100, overlap_chars=120)
    all_chunks = []

    for job in jobs:
        chunks = chunker.chunk_job_document(job)
        all_chunks.extend(chunks)

    for tech_doc in competency_docs:
        chunks = chunker.chunk_job_document(tech_doc)
        all_chunks.extend(chunks)

    print(f"[+] Generated {len(all_chunks)} semantic chunks from {len(jobs) + len(competency_docs)} documents.")

    # Write to JSONL
    with open(OUTPUT_PROCESSED_CHUNKS, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"[+] Successfully wrote all chunks to {OUTPUT_PROCESSED_CHUNKS}")


if __name__ == "__main__":
    main()
