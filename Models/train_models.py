import pandas as pd
import numpy as np
import os
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

# Ensure directories exist
os.makedirs("Models", exist_ok=True)
os.makedirs("Frontend/public/data", exist_ok=True)

CLEANED_JOBS_PATH = "Datasets/cleaned_jobs.csv"
STUDENTS_PATH = "Datasets/student_profiles.csv"

# Master skill list
ALL_SKILLS = [
    "Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker",
    "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js",
    "Node.js", "Express", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC",
    "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization",
    "R", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "MLOps", "Kubernetes", "AWS",
    "CI/CD", "Terraform", "Linux", "Bash", "Jenkins", "Product Roadmap", "Agile", "User Research",
    "Scrum", "Analytics", "Wireframing"
]

def train_salary_model():
    print("Training Ridge Salary Prediction Model...")
    df = pd.read_csv(CLEANED_JOBS_PATH)
    
    df = df.dropna(subset=["salary_avg", "standard_title", "clean_experience", "clean_location"])
    
    # 1. Encode Categoricals
    cat_cols = ["standard_title", "clean_experience", "clean_location"]
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    cat_encoded = encoder.fit_transform(df[cat_cols])
    cat_feature_names = encoder.get_feature_names_out(cat_cols)
    cat_df = pd.DataFrame(cat_encoded, columns=cat_feature_names, index=df.index)
    
    # 2. Multi-hot Encode Skills
    skills_dummies = pd.DataFrame(0, index=df.index, columns=ALL_SKILLS)
    for idx, row in df.iterrows():
        skills = [s.strip() for s in str(row["clean_skills_str"]).split(",") if s.strip()]
        skills_dummies.loc[idx, [s for s in skills if s in ALL_SKILLS]] = 1
        
    X = pd.concat([cat_df, skills_dummies], axis=1)
    y = df["salary_avg"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Ridge Regressor (extremely fast and highly interpretable)
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    rmse = np.sqrt(mse)
    
    print(f"Salary Model trained. R2 Score: {r2:.4f}, RMSE: ${rmse:,.2f}")
    
    # Serialize model & encoders
    joblib.dump(model, "Models/salary_model.joblib")
    joblib.dump(encoder, "Models/salary_encoder.joblib")
    
    # Extract Feature weights as importance indicators
    importances = np.abs(model.coef_)
    features = X.columns
    importance_df = pd.DataFrame({"feature": features, "importance": importances, "coefficient": model.coef_})
    importance_df = importance_df.sort_values(by="importance", ascending=False)
    
    top_features = importance_df.head(20).to_dict(orient="records")
    
    model_stats = {
        "r2_score": float(r2),
        "rmse": float(rmse),
        "total_training_samples": int(len(X)),
        "feature_importances": top_features,
        "categories": {
            "titles": list(df["standard_title"].unique()),
            "experience": list(df["clean_experience"].unique()),
            "locations": list(df["clean_location"].unique()),
            "skills": ALL_SKILLS
        }
    }
    
    with open("Frontend/public/data/salary_model_stats.json", "w", encoding="utf-8") as f:
        json.dump(model_stats, f, indent=4)
        
    # Compile aggregates
    role_stats = df.groupby("standard_title").agg(
        avg_salary=("salary_avg", "mean"),
        min_salary=("salary_min", "min"),
        max_salary=("salary_max", "max"),
        count=("title", "count")
    ).reset_index()
    role_stats["avg_salary"] = role_stats["avg_salary"].round(0)
    
    loc_stats = df.groupby("clean_location").agg(
        avg_salary=("salary_avg", "mean"),
        count=("title", "count")
    ).reset_index()
    loc_stats["avg_salary"] = loc_stats["avg_salary"].round(0)
    
    remote_stats = df.groupby("clean_remote").agg(
        avg_salary=("salary_avg", "mean"),
        count=("title", "count")
    ).reset_index()
    remote_stats["avg_salary"] = remote_stats["avg_salary"].round(0)
    
    exp_stats = df.groupby("clean_experience").agg(
        avg_salary=("salary_avg", "mean"),
        count=("title", "count")
    ).reset_index()
    exp_stats["avg_salary"] = exp_stats["avg_salary"].round(0)
    
    all_skills_flat = [s.strip() for sublist in df["clean_skills_str"].str.split(",") for s in sublist if s.strip()]
    skill_counts = pd.Series(all_skills_flat).value_counts().reset_index()
    skill_counts.columns = ["skill", "count"]
    
    skills_by_role = {}
    for role in df["standard_title"].unique():
        role_df = df[df["standard_title"] == role]
        role_skills = [s.strip() for sublist in role_df["clean_skills_str"].str.split(",") for s in sublist if s.strip()]
        counts = pd.Series(role_skills).value_counts().head(10).reset_index()
        counts.columns = ["skill", "count"]
        skills_by_role[role] = counts.to_dict(orient="records")
        
    sample_jobs = df.head(200)[["company", "standard_title", "title", "clean_location", "clean_remote", "clean_experience", "salary_min", "salary_max", "salary_avg", "clean_skills_str"]].to_dict(orient="records")
    
    dashboard_data = {
        "role_stats": role_stats.to_dict(orient="records"),
        "location_stats": loc_stats.to_dict(orient="records"),
        "remote_stats": remote_stats.to_dict(orient="records"),
        "experience_stats": exp_stats.to_dict(orient="records"),
        "top_skills": skill_counts.head(15).to_dict(orient="records"),
        "skills_by_role": skills_by_role,
        "sample_jobs": sample_jobs,
        "totals": {
            "total_jobs": int(len(df)),
            "global_avg_salary": float(df["salary_avg"].mean()),
            "remote_ratio": float((df["clean_remote"] == "Yes").mean() * 100)
        }
    }
    
    with open("Frontend/public/data/dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=4)

def train_placement_model():
    print("Training Decision Tree Placement Classifier...")
    df = pd.read_csv(STUDENTS_PATH)
    
    X = df[["cgpa", "skills_count", "internships", "projects", "certifications"]]
    y = df["placed"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Decision Tree Classifier (extremely fast, good feature importances)
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)
    
    print(f"Placement Model trained. Accuracy: {accuracy:.4f}")
    
    # Serialize model
    joblib.dump(model, "Models/placement_model.joblib")
    
    importances = model.feature_importances_
    features = X.columns
    importance_df = pd.DataFrame({"feature": features, "importance": importances})
    importance_df = importance_df.sort_values(by="importance", ascending=False)
    
    placement_stats = {
        "accuracy": float(accuracy),
        "precision": float(report["weighted avg"]["precision"]),
        "recall": float(report["weighted avg"]["recall"]),
        "f1_score": float(report["weighted avg"]["f1-score"]),
        "feature_importances": importance_df.to_dict(orient="records")
    }
    
    with open("Frontend/public/data/placement_model_stats.json", "w", encoding="utf-8") as f:
        json.dump(placement_stats, f, indent=4)

if __name__ == "__main__":
    train_salary_model()
    train_placement_model()
print("Model training pipeline finished successfully!")
