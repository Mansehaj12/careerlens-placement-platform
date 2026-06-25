from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import re

app = FastAPI(
    title="SkillSync Job Market API",
    description="Backend API serving job market intelligence and salary predictions.",
    version="1.0.0"
)

# Enable CORS for React frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to data assets
STATS_PATH = "frontend/public/data/market_stats.json"
MODEL_PATH = "frontend/public/data/salary_model.json"
JOBS_PATH = "frontend/public/data/cleaned_jobs_sample.json"

# Models for Request Validation
class SalaryPredictionRequest(BaseModel):
    role: str
    experience: str
    location: str
    skills: List[str]

class SalaryPredictionResponse(BaseModel):
    predicted_salary: float
    typical_range_min: float
    typical_range_max: float
    selected_role: str
    selected_experience: str
    selected_location: str
    selected_skills: List[str]
    factor_breakdown: dict

class ResumeAnalysisRequest(BaseModel):
    role: str
    resume_text: str

class ResumeAnalysisResponse(BaseModel):
    score: int
    category: str
    critique: str
    skills_found: List[str]
    skills_missing: List[str]
    roadmap: List[dict]

# Load functions
def load_json_file(file_path):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"Data file not found at {file_path}. Please run clean_and_analyze.py first.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/")
def read_root():
    return {"message": "Welcome to SkillSync API. Visit /docs for documentation."}

@app.get("/api/stats")
def get_stats():
    """Retrieve pre-calculated job market statistics."""
    return load_json_file(STATS_PATH)

@app.get("/api/jobs")
def get_jobs_sample(role: Optional[str] = None, location: Optional[str] = None):
    """Retrieve sample cleaned job records with optional filtering."""
    jobs = load_json_file(JOBS_PATH)
    if role:
        jobs = [j for j in jobs if j["standard_title"].lower() == role.lower()]
    if location:
        jobs = [j for j in jobs if j["clean_location"].lower() == location.lower()]
    return jobs[:50]  # Cap at 50 records

@app.post("/api/predict-salary", response_model=SalaryPredictionResponse)
def predict_salary(req: SalaryPredictionRequest):
    """Calculate predicted salary using the trained Ridge regression coefficients."""
    model = load_json_file(MODEL_PATH)
    
    intercept = model["intercept"]
    coefs = model["coefficients"]
    
    # Calculate Ridge prediction: intercept + coeff(Role) + coeff(Exp) + coeff(Loc) + sum(coeff(Skills))
    predicted = intercept
    breakdown = {"base_intercept": round(intercept, 2)}
    
    # 1. Role
    role_key = f"standard_title_{req.role}"
    if role_key in coefs:
        predicted += coefs[role_key]
        breakdown["role_factor"] = round(coefs[role_key], 2)
    else:
        breakdown["role_factor"] = 0.0
        
    # 2. Experience
    exp_key = f"clean_experience_{req.experience}"
    if exp_key in coefs:
        predicted += coefs[exp_key]
        breakdown["experience_factor"] = round(coefs[exp_key], 2)
    else:
        breakdown["experience_factor"] = 0.0
        
    # 3. Location
    loc_key = f"clean_location_{req.location}"
    if loc_key in coefs:
        predicted += coefs[loc_key]
        breakdown["location_factor"] = round(coefs[loc_key], 2)
    else:
        breakdown["location_factor"] = 0.0
        
    # 4. Skills
    skills_factor = 0.0
    skills_breakdown = {}
    for skill in req.skills:
        if skill in coefs:
            skills_factor += coefs[skill]
            skills_breakdown[skill] = round(coefs[skill], 2)
            
    predicted += skills_factor
    breakdown["skills_total_factor"] = round(skills_factor, 2)
    breakdown["skills_breakdown"] = skills_breakdown
    
    # Enforce minimum lower bound
    final_salary = max(30000.0, round(predicted, 2))
    
    return SalaryPredictionResponse(
        predicted_salary=final_salary,
        typical_range_min=round(final_salary * 0.9, 2),
        typical_range_max=round(final_salary * 1.1, 2),
        selected_role=req.role,
        selected_experience=req.experience,
        selected_location=req.location,
        selected_skills=req.skills,
        factor_breakdown=breakdown
    )

@app.post("/api/analyze-resume", response_model=ResumeAnalysisResponse)
def analyze_resume(req: ResumeAnalysisRequest):
    """Analyze resume text and extract matching skills and gaps."""
    stats = load_json_file(STATS_PATH)
    
    role_skills_data = stats["skills_by_role"].get(req.role, [])
    if not role_skills_data:
        raise HTTPException(status_code=400, detail=f"No skills data available for role: {req.role}")
        
    text_lower = req.resume_text.lower()
    skills_found = []
    skills_missing = []
    weighted_score_sum = 0.0
    total_weight_sum = 0.0
    
    for skill_obj in role_skills_data:
        skill_name = skill_obj["skill"]
        weight = skill_obj["count"]
        total_weight_sum += weight
        
        # Word boundary pattern match
        pattern = r'\b' + re.escape(skill_name.lower()) + r'\b'
        if skill_name.lower() in ['c++', 'next.js', 'node.js', 'ci/cd', 'a/b testing', 'html5', 'css3']:
            pattern = re.escape(skill_name.lower())
            
        if re.search(pattern, text_lower):
            skills_found.append(skill_name)
            weighted_score_sum += weight
        else:
            skills_missing.append(skill_name)
            
    score = round((weighted_score_sum / total_weight_sum) * 100) if total_weight_sum > 0 else 0
    
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
    
    critique = ""
    category = ""
    if score < 35:
        category = "Critical Alignment Gap"
        critique = "Your resume shows a strong mismatch for this role. You are missing key technological foundations. We recommend building 2-3 targeted projects using the missing technologies and documenting them on GitHub before applying."
    elif score >= 35 and score < 70:
        category = "Competitive Profile"
        critique = "You possess solid core skills, but you are missing several secondary tools that distinguish premium candidates. Adding minor keyword modifications and highlighting hands-on experiences with containerization or SQL querying will significantly boost screening rates."
    else:
        category = "Highly Matched Talent"
        critique = "Excellent skill alignment! Your resume effectively matches market demand. To stand out even further to human recruiters, focus on showcasing quantified achievements (e.g., 'reduced query times by 40%') rather than just listing technologies."
        
    return ResumeAnalysisResponse(
        score=score,
        category=category,
        critique=critique,
        skills_found=skills_found,
        skills_missing=skills_missing,
        roadmap=roadmap
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
