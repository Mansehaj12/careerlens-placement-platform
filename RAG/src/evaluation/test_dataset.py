"""
Golden Evaluation Benchmark Dataset for CareerLens AI
Contains standardized evaluation queries, candidate profiles, and ground-truth expectations
for automated RAG evaluation (Context Precision, Recall, and Faithfulness).
"""

GOLDEN_TEST_CASES = [
    {
        "id": "eval_01_fresher_ml",
        "query": "I am a fresher seeking Junior Machine Learning Engineer roles. I know Python, PyTorch, and SQL. What are my top skill gaps?",
        "candidate_profile": "Education: B.Tech CSE. Experience: 0.5 yrs. Skills: Python, PyTorch, Scikit-Learn, SQL, Git. Projects: ML salary prediction, Image classification.",
        "target_category": "Data Science & AI",
        "ground_truth_skills": ["Python", "PyTorch", "Machine Learning", "SQL"],
        "ground_truth_expected_gaps": ["Docker", "MLOps", "Model Deployment", "FastAPI", "Kubernetes"],
        "ground_truth_answer": "Based on retrieved industry postings, the candidate matches core ML foundations (Python, PyTorch, SQL), but exhibits critical gaps in production engineering: containerization (Docker), API serving (FastAPI), and MLOps deployment."
    },
    {
        "id": "eval_02_backend_engineer",
        "query": "I have 3 years experience in Python, Django, and PostgreSQL. What do senior backend roles require that I am missing?",
        "candidate_profile": "Experience: 3.5 yrs. Current Stack: Python, FastAPI, Django, PostgreSQL, Redis. Target: Senior Backend Software Engineer.",
        "target_category": "Backend & Software Engineering",
        "ground_truth_skills": ["Python", "Django", "PostgreSQL", "FastAPI"],
        "ground_truth_expected_gaps": ["Kubernetes", "System Design", "Microservices", "gRPC", "Kafka"],
        "ground_truth_answer": "Senior backend postings require architecture and scale capabilities beyond web frameworks: distributed messaging (Kafka/RabbitMQ), container orchestration (Kubernetes), and high-throughput system design."
    },
    {
        "id": "eval_03_data_analyst",
        "query": "What are the core tools required for Data Analyst and Business Intelligence positions?",
        "candidate_profile": "Target: Data Analyst. Skills: SQL, Power BI, Excel, Pandas.",
        "target_category": "Data Analytics & BI",
        "ground_truth_skills": ["SQL", "Power BI", "Excel", "Data Visualization"],
        "ground_truth_expected_gaps": ["Tableau", "Statistics", "A/B Testing", "Data Warehousing"],
        "ground_truth_answer": "Data analyst roles require SQL query optimization, Power BI / Tableau dashboarding, executive storytelling, and statistical A/B testing methodologies."
    },
    {
        "id": "eval_04_devops_cloud",
        "query": "What qualifications are mandatory for AWS Cloud and DevOps engineers?",
        "candidate_profile": "Target: DevOps Engineer. Skills: Linux, Bash, Git, Docker.",
        "target_category": "DevOps & Cloud",
        "ground_truth_skills": ["Linux", "Docker", "Git"],
        "ground_truth_expected_gaps": ["Kubernetes", "Terraform", "AWS", "CI/CD", "Monitoring/Prometheus"],
        "ground_truth_answer": "Mandatory DevOps competencies include Infrastructure as Code (Terraform), container orchestration (Kubernetes), cloud providers (AWS), and CI/CD pipeline automation."
    }
]
