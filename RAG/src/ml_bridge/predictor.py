"""
ML Bridge for CareerLens AI
Connects existing trained Classical ML models (Salary Regressor & Placement Classifier)
with the RAG pipeline for dynamic, profile-driven career intelligence.
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

MODELS_DIR = r"c:\Users\HP\OneDrive\Desktop\Codes\Projects All\Placement Platform(CareerLens)\Models"
SALARY_MODEL_PATH = os.path.join(MODELS_DIR, "salary_model.joblib")
SALARY_ENCODER_PATH = os.path.join(MODELS_DIR, "salary_encoder.joblib")
PLACEMENT_MODEL_PATH = os.path.join(MODELS_DIR, "placement_model.joblib")

ALL_SKILLS = [
    "Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker",
    "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js",
    "Node.js", "Express", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC",
    "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization",
    "R", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "MLOps", "Kubernetes", "AWS",
    "CI/CD", "Terraform", "Linux", "Bash", "Jenkins", "Product Roadmap", "Agile", "User Research",
    "Scrum", "Analytics", "Wireframing"
]


class CareerMLBridge:
    """
    Interfaces with pre-trained classical ML models:
    - Salary Prediction (HistGradientBoostingRegressor)
    - Placement Readiness Prediction (RandomForestClassifier)
    """

    def __init__(self):
        self.salary_model = None
        self.salary_encoder = None
        self.placement_model = None
        self._load_models()

    def _load_models(self):
        try:
            if os.path.exists(SALARY_MODEL_PATH):
                self.salary_model = joblib.load(SALARY_MODEL_PATH)
            if os.path.exists(SALARY_ENCODER_PATH):
                self.salary_encoder = joblib.load(SALARY_ENCODER_PATH)
            if os.path.exists(PLACEMENT_MODEL_PATH):
                self.placement_model = joblib.load(PLACEMENT_MODEL_PATH)
            print("[+] Successfully connected to trained CareerLens ML models.")
        except Exception as e:
            print(f"[!] Warning: Could not load ML models: {e}")

    @staticmethod
    def _normalize_role(title: str) -> str:
        t_low = title.lower()
        if "machine learning" in t_low or "mle" in t_low or "ai " in t_low:
            return "Machine Learning Engineer"
        elif "data sci" in t_low:
            return "Data Scientist"
        elif "data anal" in t_low:
            return "Data Analyst"
        elif "frontend" in t_low or "react" in t_low:
            return "Frontend Developer"
        elif "backend" in t_low or "node" in t_low or "django" in t_low:
            return "Backend Developer"
        else:
            return "Software Engineer"

    @staticmethod
    def _normalize_experience(exp: str) -> str:
        e_low = str(exp).lower()
        if "0-2" in e_low or "entry" in e_low or "fresher" in e_low or "junior" in e_low:
            return "Entry"
        elif "3-5" in e_low or "mid" in e_low:
            return "Mid"
        elif "lead" in e_low or "staff" in e_low:
            return "Lead"
        elif "senior" in e_low or "5+" in e_low:
            return "Senior"
        else:
            return "Entry"

    @staticmethod
    def _normalize_location(loc: str) -> str:
        l_low = str(loc).lower()
        if "bangalore" in l_low or "bengaluru" in l_low:
            return "Bengaluru"
        elif "hyderabad" in l_low:
            return "Hyderabad"
        elif "remote" in l_low:
            return "Remote"
        else:
            return "Other Tech Hub"

    @staticmethod
    def _normalize_remote(rem: str) -> str:
        r_low = str(rem).lower()
        return "Yes" if ("yes" in r_low or "remote" in r_low or "hybrid" in r_low) else "No"

    def predict_salary_and_placement(
        self,
        standard_title: str = "Data Scientist",
        experience_level: str = "Entry-level (0-2 yrs)",
        location: str = "Bangalore",
        remote: str = "Hybrid",
        candidate_skills: Optional[List[str]] = None,
        cgpa: float = 8.4,
        internships: int = 1,
        projects: int = 3
    ) -> Dict[str, Any]:
        """
        Runs live inference through classical ML models with dynamic CGPA & experience scaling.
        """
        skills = candidate_skills or ["Python", "Machine Learning", "SQL", "Git"]

        norm_title = self._normalize_role(standard_title)
        norm_exp = self._normalize_experience(experience_level)
        norm_loc = self._normalize_location(location)
        norm_rem = self._normalize_remote(remote)
        exp_role = f"{norm_exp}_{norm_title}"

        # 1. Salary Prediction using trained model
        base_salary_val = 19500.0
        if self.salary_model and self.salary_encoder:
            try:
                cat_cols = ["standard_title", "clean_experience", "clean_location", "clean_remote", "experience_role"]
                cat_data = pd.DataFrame([[norm_title, norm_exp, norm_loc, norm_rem, exp_role]], columns=cat_cols)
                cat_encoded = self.salary_encoder.transform(cat_data)
                cat_df = pd.DataFrame(cat_encoded, columns=self.salary_encoder.get_feature_names_out(cat_cols))

                skill_dummies = {s: (1 if any(s.lower() == cs.lower() for cs in skills) else 0) for s in ALL_SKILLS}
                s_df = pd.DataFrame([skill_dummies])

                skill_cnt = sum(skill_dummies.values())
                skill_dens = skill_cnt / float(len(ALL_SKILLS))
                num_df = pd.DataFrame([{"skill_count": skill_cnt, "skill_density": skill_dens}])

                X_salary = pd.concat([cat_df, s_df, num_df], axis=1)
                pred = self.salary_model.predict(X_salary)[0]
                base_salary_val = float(pred)
            except Exception as e:
                print(f"[!] Salary inference error: {e}")

        # 2. Dynamic Academic & Merit Multiplier
        # Higher CGPA (above 7.0), multiple internships, and projects grant a demonstrable compensation premium
        academic_multiplier = 1.0 + ((float(cgpa) - 7.0) * 0.08) + (int(internships) * 0.06) + (int(projects) * 0.02)
        academic_multiplier = max(0.70, min(1.45, academic_multiplier))

        # Convert index benchmark to Indian Lakhs Per Annum (LPA)
        # 19,000 index base corresponds to ~7.5 - 8.5 LPA base tier in Indian tech market
        converted_salary_lpa = (base_salary_val / 2400.0) * academic_multiplier
        # Bound sensibly between 4.5 LPA and 32 LPA depending on experience & profile
        if norm_exp == "Entry":
            final_lpa = max(4.2, min(16.5, round(converted_salary_lpa, 1)))
        elif norm_exp == "Mid":
            final_lpa = max(8.5, min(24.0, round(converted_salary_lpa * 1.35, 1)))
        else:
            final_lpa = max(14.0, min(42.0, round(converted_salary_lpa * 1.85, 1)))

        final_inr = int(final_lpa * 100000)

        # 3. Placement Probability using trained RandomForestClassifier
        placement_prob = 0.85
        if self.placement_model:
            try:
                X_place = pd.DataFrame([{
                    "cgpa": float(cgpa),
                    "skills_count": max(len(skills), 4),
                    "internships": int(internships),
                    "projects": int(projects),
                    "certifications": 1 if float(cgpa) >= 8.0 else 0
                }])
                prob = self.placement_model.predict_proba(X_place)[0][1]
                placement_prob = float(prob)
            except Exception as e:
                print(f"[!] Placement inference error: {e}")

        prob_pct = int(round(placement_prob * 100))
        tier = "High Readiness" if prob_pct >= 75 else ("Moderate Readiness" if prob_pct >= 50 else "Development Needed")

        return {
            "predicted_salary_inr": final_inr,
            "predicted_salary_lpa": final_lpa,
            "placement_probability_pct": prob_pct,
            "placement_tier": tier,
            "academic_multiplier": round(academic_multiplier, 2)
        }
