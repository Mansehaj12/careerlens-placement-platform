from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import joblib
import pandas as pd
import numpy as np
import io
from dotenv import load_dotenv

# Ensure Backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load env variables
dotenv_path = os.path.join(backend_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Import database and parser helper modules
import database
import parser

app = Flask(__name__)
# Enable CORS for React frontend (default port 5173 or other hosts)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Paths to models and metadata relative to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SALARY_MODEL_PATH = os.path.join(BASE_DIR, "Models", "salary_model.joblib")
SALARY_ENCODER_PATH = os.path.join(BASE_DIR, "Models", "salary_encoder.joblib")
PLACEMENT_MODEL_PATH = os.path.join(BASE_DIR, "Models", "placement_model.joblib")
DASHBOARD_DATA_PATH = os.path.join(BASE_DIR, "frontend", "public", "data", "dashboard_data.json")
QUALITY_DATA_PATH = os.path.join(BASE_DIR, "frontend", "public", "data", "data_quality.json")
PLACEMENT_STATS_PATH = os.path.join(BASE_DIR, "frontend", "public", "data", "placement_model_stats.json")
SALARY_STATS_PATH = os.path.join(BASE_DIR, "frontend", "public", "data", "salary_model_stats.json")
BENCHMARK_DATA_PATH = os.path.join(BASE_DIR, "frontend", "public", "data", "model_benchmarks.json")

# Global model placeholders loaded on startup
salary_model = None
salary_encoder = None
placement_model = None
dashboard_data = None
quality_data = None
placement_stats = None
salary_stats = None
benchmark_data = None

def load_models():
    global salary_model, salary_encoder, placement_model, dashboard_data, quality_data, placement_stats, salary_stats, benchmark_data
    print("Loading models and analytics datasets on startup...")
    
    # Initialize database and seed tables
    database.init_db()
    
    if os.path.exists(SALARY_MODEL_PATH):
        salary_model = joblib.load(SALARY_MODEL_PATH)
    if os.path.exists(SALARY_ENCODER_PATH):
        salary_encoder = joblib.load(SALARY_ENCODER_PATH)
    if os.path.exists(PLACEMENT_MODEL_PATH):
        placement_model = joblib.load(PLACEMENT_MODEL_PATH)
        
    if os.path.exists(DASHBOARD_DATA_PATH):
        with open(DASHBOARD_DATA_PATH, "r", encoding="utf-8") as f:
            dashboard_data = json.load(f)
    if os.path.exists(QUALITY_DATA_PATH):
        with open(QUALITY_DATA_PATH, "r", encoding="utf-8") as f:
            quality_data = json.load(f)
    if os.path.exists(PLACEMENT_STATS_PATH):
        with open(PLACEMENT_STATS_PATH, "r", encoding="utf-8") as f:
            placement_stats = json.load(f)
    if os.path.exists(SALARY_STATS_PATH):
        with open(SALARY_STATS_PATH, "r", encoding="utf-8") as f:
            salary_stats = json.load(f)
    if os.path.exists(BENCHMARK_DATA_PATH):
        with open(BENCHMARK_DATA_PATH, "r", encoding="utf-8") as f:
            benchmark_data = json.load(f)

# API Routes
@app.route("/", methods=["GET"])
def check_status():
    return jsonify({
        "status": "online",
        "service": "CareerLens API Engine",
        "version": "1.1.0",
        "db_connected": database.check_connection()
    })

@app.route("/api/market/stats", methods=["GET"])
def get_market_stats():
    """Serves the job market statistics and data pipeline quality reports."""
    if not dashboard_data or not quality_data:
        return jsonify({"error": "Stats data files not found. Run ML training pipeline first."}), 500
        
    return jsonify({
        "dashboard": dashboard_data,
        "quality": quality_data
    })

@app.route("/api/models/benchmark", methods=["GET"])
def get_model_benchmarks():
    """Serves the 5-fold cross-validation benchmarking comparison across all models."""
    if not benchmark_data:
        return jsonify({"error": "Benchmark data not found. Run ML training pipeline first."}), 500
        
    return jsonify(benchmark_data)

@app.route("/api/predict/salary", methods=["POST"])
def predict_salary():
    """Predict expected salary based on title, experience, location, remote status, and selected skills."""
    if not salary_model or not salary_encoder:
        return jsonify({"error": "Salary ML models are not loaded."}), 500
        
    try:
        data = request.get_json() or {}
        role = str(data.get("role") or data.get("job_title") or "Software Engineer")
        
        exp_val = data.get("experience", "Mid")
        if isinstance(exp_val, (int, float)):
            if exp_val < 2:
                experience = "Entry"
            elif exp_val <= 5:
                experience = "Mid"
            else:
                experience = "Lead"
        else:
            experience = str(exp_val)
            
        location = str(data.get("location", "Bengaluru"))
        
        remote_val = data.get("remote", "No")
        if isinstance(remote_val, bool):
            remote = "Yes" if remote_val else "No"
        elif str(remote_val).lower() in ["true", "yes", "1"]:
            remote = "Yes"
        else:
            remote = "No"
            
        skills = data.get("skills", [])
        experience_role = f"{experience}_{role}"
        
        # 1. One-hot encode categoricals matching training columns
        cat_cols = ["standard_title", "clean_experience", "clean_location", "clean_remote", "experience_role"]
        cat_df = pd.DataFrame([[role, experience, location, remote, experience_role]], columns=cat_cols, dtype=object)
        cat_encoded = salary_encoder.transform(cat_df)
        cat_feature_names = salary_encoder.get_feature_names_out(cat_cols)
        cat_encoded_df = pd.DataFrame(cat_encoded, columns=cat_feature_names)
        
        # 2. Multi-hot encode skills
        skills_dummies = pd.DataFrame(0, index=[0], columns=parser.ALL_SKILLS)
        for s in skills:
            if s in parser.ALL_SKILLS:
                skills_dummies.loc[0, s] = 1
                
        # 3. Numeric features: skill_count and skill_density
        skill_count = sum(1 for s in skills if s in parser.ALL_SKILLS)
        skill_density = skill_count / float(len(parser.ALL_SKILLS))
        num_df = pd.DataFrame({"skill_count": [skill_count], "skill_density": [skill_density]})
        
        # 4. Concatenate and predict
        X_pred = pd.concat([cat_encoded_df, skills_dummies, num_df], axis=1)
        predicted_val = salary_model.predict(X_pred)[0]
        
        # Bounded salary estimation
        final_salary = max(1000.0, round(predicted_val, 2))
        
        # Empirical prediction range from 5-fold CV validation MAE
        empirical_margin = 5215.74
        if salary_stats and "empirical_margin_mae" in salary_stats:
            empirical_margin = float(salary_stats["empirical_margin_mae"])
            
        range_min = max(500.0, round(final_salary - empirical_margin, 2))
        range_max = round(final_salary + empirical_margin, 2)
        
        return jsonify({
            "predicted_salary": final_salary,
            "typical_range_min": range_min,
            "typical_range_max": range_max,
            "empirical_margin": empirical_margin,
            "range_type": "Empirical Prediction Range (+/- Validation MAE)",
            "percentile": round(get_salary_percentile(final_salary), 1)
        })
    except Exception as e:
        return jsonify({"error": f"Salary prediction error: {str(e)}"}), 400

@app.route("/api/predict/placement", methods=["POST"])
def predict_placement():
    """Classifies placement likelihood and returns improvement recommendations."""
    if not placement_model:
        return jsonify({"error": "Placement ML model is not loaded."}), 500
        
    try:
        data = request.get_json()
        cgpa = float(data.get("cgpa", 0.0))
        skills_count = int(data.get("skills_count", 0))
        internships = int(data.get("internships", 0))
        projects = int(data.get("projects", 0))
        certifications = int(data.get("certifications", 0))
        
        # Format for input
        X_pred = pd.DataFrame([[cgpa, skills_count, internships, projects, certifications]], 
                              columns=["cgpa", "skills_count", "internships", "projects", "certifications"])
                              
        # Predict probability of placement
        # classes: 0 = not placed, 1 = placed
        prob = placement_model.predict_proba(X_pred)[0][1]
        
        # Calculate scores
        employability_score = round(prob * 100)
        
        # Formulate actionable suggestions
        suggestions = []
        if cgpa < 7.5:
            suggestions.append("Academic Filter: Your CGPA is below the typical 7.5 threshold for premier companies. Focus on lifting your academic standing in upcoming terms.")
        if internships == 0:
            suggestions.append("Experience Gap: Highlight active involvement in virtual internships, open-source programs, or freelancing to get your first professional milestone on paper.")
        if projects < 2:
            suggestions.append("Project Portfolio: Recruiters look for at least 2 comprehensive full-stack/data-engineering projects. Ensure yours are hosted on GitHub with detailed READMEs.")
        if certifications == 0:
            suggestions.append("Skills Validation: Acquire cloud/data certifications (e.g. AWS Certified Practitioner, Snowflake, or Google Data Engineer) to validate your tech stack to automated screeners.")
            
        if len(suggestions) == 0:
            suggestions.append("Profile is highly competitive! Focus on refining your system design and coding mock interviews to clear final rounds.")
            
        return jsonify({
            "placement_probability": round(prob, 3),
            "employability_score": employability_score,
            "suggestions": suggestions,
            "feature_importance": placement_stats.get("feature_importances", []) if placement_stats else []
        })
    except Exception as e:
        return jsonify({"error": f"Placement prediction error: {str(e)}"}), 400

@app.route("/api/analyze/resume", methods=["POST"])
def analyze_resume():
    """Extract skills from uploaded PDF resume or text and run comprehensive ATS 2.0 gap analysis."""
    text = ""
    role = "Software Engineer"
    
    # Support both multipart form file upload and direct text JSON/form submissions
    if "file" in request.files and request.files["file"].filename != "":
        file = request.files["file"]
        role = request.form.get("role", "Software Engineer")
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Invalid format. Resume must be a PDF file."}), 400
        try:
            file_bytes = io.BytesIO(file.read())
            text = parser.extract_text_from_pdf(file_bytes)
        except Exception as e:
            return jsonify({"error": f"Failed to extract text from PDF: {str(e)}"}), 400
    elif request.is_json:
        data = request.get_json() or {}
        text = data.get("text") or data.get("resume_text") or ""
        role = data.get("role") or data.get("target_role") or "Software Engineer"
    elif "text" in request.form or "resume_text" in request.form:
        text = request.form.get("text") or request.form.get("resume_text") or ""
        role = request.form.get("role") or request.form.get("target_role") or "Software Engineer"
    else:
        return jsonify({"error": "No resume file or text content provided."}), 400
        
    if not text.strip():
        return jsonify({"error": "Could not extract readable text. Ensure the file contains selectable text rather than scanned images."}), 400
        
    try:
        # 1. Parse tech skills & domain categorization
        skills_found = parser.extract_skills_from_text(text)
        categorized_skills = parser.categorize_skills(skills_found)
        
        # 2. ATS Audits
        section_audit = parser.audit_resume_sections(text)
        metrics_audit = parser.audit_quantifiable_metrics(text)
        verbs_audit = parser.audit_action_verbs(text)
        
        # 3. Target role skills comparison using rigorous domain taxonomy
        if role in parser.ROLE_SKILL_REQUIREMENTS:
            required_skills = parser.ROLE_SKILL_REQUIREMENTS[role]
        elif dashboard_data and "skills_by_role" in dashboard_data and role in dashboard_data["skills_by_role"]:
            required_skills = [s["skill"] for s in dashboard_data["skills_by_role"][role]]
        else:
            required_skills = ["Python", "SQL", "Git"]
            
        skills_missing = [s for s in required_skills if s not in skills_found]
        intersection = [s for s in required_skills if s in skills_found]
        match_percentage = round((len(intersection) / len(required_skills)) * 100) if required_skills else 0
        
        # 4. Composite ATS Readiness Score
        ats_readiness = parser.compute_ats_readiness(
            match_percentage,
            section_audit["section_score"],
            metrics_audit["score"],
            verbs_audit["score"]
        )
        
        course_recommendations = {
            "Python": "Python for Data Science (Kaggle / Coursera)",
            "SQL": "Complete SQL Bootcamp (Udemy / LeetCode Database)",
            "React": "React Documentation Tutorials & FreeCodeCamp Full Course",
            "AWS": "AWS Certified Cloud Practitioner Pathway",
            "Docker": "Docker & Kubernetes Containerization Fundamentals (Docker Labs)",
            "Tableau": "Data Visualization Specialist Course (Tableau eLearning)",
            "Power BI": "Microsoft PL-300 Business Analyst Certification Pathway",
            "Machine Learning": "Introduction to Machine Learning (Andrew Ng on Coursera)",
            "System Design": "System Design Primer & Designing Data-Intensive Applications",
            "CI/CD": "DevOps Foundations: Continuous Integration & Deployment (GitHub Actions)",
            "Kubernetes": "Certified Kubernetes Administrator (CKA) Training"
        }
        
        roadmap = [
            {"skill": s, "resource": course_recommendations.get(s, f"Advanced {s} Guides & Project Building")}
            for s in skills_missing
        ]
        
        # Tailored critique
        if match_percentage < 35:
            category = "Critical Alignment Gap"
            critique = "Your resume shows a strong mismatch for this role. Key technical foundations are missing. Build 2-3 focused projects using these tools."
        elif match_percentage >= 35 and match_percentage < 70:
            category = "Competitive Profile"
            critique = "Solid foundational competencies. Adding hands-on cloud/database tools and quantifying achievements will elevate your callback rate."
        else:
            category = "Highly Matched Talent"
            critique = "Outstanding technical alignment! Focus on showcasing quantified impact and high-scale metrics to clear executive screening rounds."
            
        return jsonify({
            "evaluated_role": role,
            "extracted_text": text,
            "match_percentage": match_percentage,
            "category": category,
            "critique": critique,
            "skills_found": [s for s in skills_found if s in required_skills],
            "all_extracted_skills": skills_found,
            "skills_missing": skills_missing,
            "categorized_skills": categorized_skills,
            "roadmap": roadmap,
            "ats_audit": {
                "overall_score": ats_readiness["overall_score"],
                "grade": ats_readiness["grade"],
                "verdict": ats_readiness["verdict"],
                "section_audit": section_audit,
                "metrics_audit": metrics_audit,
                "verbs_audit": verbs_audit
            }
        })
    except Exception as e:
        return jsonify({"error": f"Resume analysis error: {str(e)}"}), 500

def get_salary_percentile(salary):
    """Estimate salary market percentile compared to global average."""
    # Updated mean and std for the Indian tech market scale
    mean = 24228.35
    std = 7506.26
    z = (salary - mean) / std
    # Cumulative probability approximation
    prob = 1 / (1 + np.exp(-0.07056 * z**3 - 1.5976 * z))
    return min(99.9, max(0.1, prob * 100))

# Load models and initialize DB on module import (required for WSGI/production servers)
load_models()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
