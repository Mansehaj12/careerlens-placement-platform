from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import joblib
import pandas as pd
import numpy as np
import io
from dotenv import load_dotenv

# Load env variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
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

# Global model placeholders loaded on startup
salary_model = None
salary_encoder = None
placement_model = None
dashboard_data = None
quality_data = None
placement_stats = None

def load_models():
    global salary_model, salary_encoder, placement_model, dashboard_data, quality_data, placement_stats
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

# API Routes
@app.route("/", methods=["GET"])
def check_status():
    return jsonify({
        "status": "online",
        "service": "CareerLens API Engine",
        "version": "1.0.0",
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

@app.route("/api/predict/salary", methods=["POST"])
def predict_salary():
    """Predict expected salary based on title, experience, location, and selected skills."""
    if not salary_model or not salary_encoder:
        return jsonify({"error": "Salary ML models are not loaded."}), 500
        
    try:
        data = request.get_json()
        role = data.get("role")
        experience = data.get("experience")
        location = data.get("location")
        skills = data.get("skills", [])
        
        # 1. One-hot encode categoricals matching training columns
        cat_df = pd.DataFrame([[role, experience, location]], columns=["standard_title", "clean_experience", "clean_location"])
        cat_encoded = salary_encoder.transform(cat_df)
        cat_feature_names = salary_encoder.get_feature_names_out(["standard_title", "clean_experience", "clean_location"])
        cat_encoded_df = pd.DataFrame(cat_encoded, columns=cat_feature_names)
        
        # 2. Multi-hot encode skills
        skills_dummies = pd.DataFrame(0, index=[0], columns=parser.ALL_SKILLS)
        for s in skills:
            if s in parser.ALL_SKILLS:
                skills_dummies.loc[0, s] = 1
                
        # 3. Concatenate and predict
        X_pred = pd.concat([cat_encoded_df, skills_dummies], axis=1)
        predicted_val = salary_model.predict(X_pred)[0]
        
        # Bounded salary estimation
        final_salary = max(1000.0, round(predicted_val, 2))
        
        return jsonify({
            "predicted_salary": final_salary,
            "typical_range_min": round(final_salary * 0.9, 2),
            "typical_range_max": round(final_salary * 1.1, 2),
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
    """Extract skills from uploaded PDF resume and run gap analysis against target role."""
    if "file" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400
        
    file = request.files["file"]
    role = request.form.get("role", "Software Engineer")
    
    if file.filename == "":
        return jsonify({"error": "Selected file is empty."}), 400
        
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Invalid format. Resume must be a PDF file."}), 400
        
    try:
        # Extract text from file stream bytes
        file_bytes = io.BytesIO(file.read())
        text = parser.extract_text_from_pdf(file_bytes)
        
        if not text.strip():
            return jsonify({"error": "Could not extract readable text from PDF. Ensure the file contains selectable text rather than scanned images."}), 400
            
        # Parse skills
        skills_found = parser.extract_skills_from_text(text)
        
        # Get target role required skills from dashboard_data
        role_skills_data = []
        if dashboard_data and "skills_by_role" in dashboard_data:
            role_skills_data = dashboard_data["skills_by_role"].get(role, [])
            
        required_skills = [s["skill"] for s in role_skills_data]
        if not required_skills:
            # fallback defaults
            default_mapping = {
                "Software Engineer": ["Python", "Java", "Git", "SQL", "Docker", "C++", "System Design"],
                "Frontend Developer": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Tailwind", "Next.js"],
                "Backend Developer": ["Node.js", "Express", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC"],
                "Data Analyst": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing"],
                "Data Scientist": ["Python", "SQL", "Pandas", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "Statistics"],
                "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "MLOps", "Docker", "Kubernetes", "AWS"]
            }
            required_skills = default_mapping.get(role, ["Python", "SQL", "Git"])
            
        skills_missing = [s for s in required_skills if s not in skills_found]
        
        # Compute match percentage based on count intersection
        intersection = [s for s in required_skills if s in skills_found]
        match_percentage = round((len(intersection) / len(required_skills)) * 100) if required_skills else 0
        
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
        
        # Actionable critique
        if match_percentage < 35:
            category = "Critical Alignment Gap"
            critique = "Your resume shows a strong mismatch for this role. You are missing key technological foundations. We recommend building 2-3 targeted projects using the missing technologies and documenting them on GitHub before applying."
        elif match_percentage >= 35 and match_percentage < 70:
            category = "Competitive Profile"
            critique = "You possess solid core skills, but you are missing several secondary tools that distinguish premium candidates. Adding minor keyword modifications and highlighting hands-on experiences with containerization or SQL querying will significantly boost screening rates."
        else:
            category = "Highly Matched Talent"
            critique = "Excellent skill alignment! Your resume effectively matches market demand. To stand out even further to human recruiters, focus on showcasing quantified achievements (e.g., 'reduced query times by 40%') rather than just listing technologies."
            
        return jsonify({
            "match_percentage": match_percentage,
            "category": category,
            "critique": critique,
            "skills_found": [s for s in skills_found if s in required_skills],
            "all_extracted_skills": skills_found,
            "skills_missing": skills_missing,
            "roadmap": roadmap
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

if __name__ == "__main__":
    load_models()
    app.run(host="127.0.0.1", port=5000, debug=True)
