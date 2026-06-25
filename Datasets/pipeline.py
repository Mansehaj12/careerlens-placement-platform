import pandas as pd
import numpy as np
import os
import re
import json

RAW_JOBS_PATH = "Datasets/raw_jobs.csv"
CLEANED_JOBS_PATH = "Datasets/cleaned_jobs.csv"
QUALITY_JSON_PATH = "Datasets/data_quality.json"
FRONTEND_DATA_DIR = "Frontend/public/data"

# Create output folders
os.makedirs("Datasets", exist_ok=True)
os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)

ALL_SKILLS = [
    "Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker",
    "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js",
    "Node.js", "Express", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC",
    "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization",
    "R", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "MLOps", "Kubernetes", "AWS",
    "CI/CD", "Terraform", "Linux", "Bash", "Jenkins", "Product Roadmap", "Agile", "User Research",
    "Scrum", "Analytics", "Wireframing"
]

def clean_experience(val):
    if pd.isna(val) or str(val).strip() == "":
        return "Not Specified"
    v = str(val).strip().title()
    if v in ["Entry", "Mid", "Senior", "Lead", "Intern", "Not Specified"]:
        return v
    return "Not Specified"

def clean_job_title(title):
    t_lower = str(title).lower()
    roles = {
        "Machine Learning Engineer": ["machine learning", "ml engineer", "ml ops", "mlops"],
        "Data Scientist": ["data scientist", "data science"],
        "Data Analyst": ["data analyst", "analytics analyst", "business analyst"],
        "Frontend Developer": ["frontend", "front-end", "ui developer"],
        "Backend Developer": ["backend", "back-end", "api developer"],
        "Software Engineer": ["software engineer", "software developer", "sde", "developer", "programmer"]
    }
    for standard_role, keywords in roles.items():
        for kw in keywords:
            if kw in t_lower:
                return standard_role
    return "Software Engineer"

def parse_salary(salary_str):
    if pd.isna(salary_str) or str(salary_str).strip() == "":
        return np.nan, np.nan
    
    s = str(salary_str).strip()
    multiplier = 1.0
    
    if "€" in s:
        multiplier = 1.1 # EUR to USD
        s = s.replace("€", "")
    elif "₹" in s:
        multiplier = 0.012 # INR to USD
        s = s.replace("₹", "")
    else:
        s = s.replace("$", "")
        
    s = s.replace(",", "")
    
    is_hourly = False
    if "/hr" in s.lower() or "hr" in s.lower() or "hour" in s.lower():
        is_hourly = True
        s = re.sub(r'(?i)/hr|hr|hour|hourly', '', s)
        
    s = re.sub(r'(?i)/yr|yr|year|annual|annually', '', s)
    s_normalized = re.sub(r'(?i)(\d+)k', r'\1000', s)
    
    found = re.findall(r'\d+', s_normalized)
    if not found:
        return np.nan, np.nan
        
    numbers = [float(n) for n in found]
    if len(numbers) >= 2:
        val_min, val_max = numbers[0], numbers[1]
    else:
        val_min = val_max = numbers[0]
        
    if is_hourly:
        val_min *= 2080
        val_max *= 2080
        
    val_min *= multiplier
    val_max *= multiplier
    
    return val_min, val_max

def extract_skills(skills_text):
    if pd.isna(skills_text):
        return []
    txt_lower = str(skills_text).lower()
    extracted = []
    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if skill in ["C++", "Next.js", "Node.js", "CI/CD", "A/B Testing", "HTML5", "CSS3"]:
            pattern = re.escape(skill.lower())
        if re.search(pattern, txt_lower):
            extracted.append(skill)
    return extracted

def run_pipeline():
    print("Running data cleaning pipeline...")
    if not os.path.exists(RAW_JOBS_PATH):
        raise FileNotFoundError(f"Raw jobs file not found at {RAW_JOBS_PATH}")
        
    df_raw = pd.read_csv(RAW_JOBS_PATH)
    
    # 1. Capture Before Metrics
    metrics_before = {
        "total_records": int(len(df_raw)),
        "missing_salaries": int(df_raw["salary"].isna().sum() + (df_raw["salary"] == "").sum() + (df_raw["salary"] == "Competitive market rate").sum()),
        "missing_locations": int(df_raw["location"].isna().sum() + (df_raw["location"] == "").sum()),
        "missing_experience": int(df_raw["experience"].isna().sum() + (df_raw["experience"] == "").sum()),
        "duplicate_records": int(df_raw.duplicated(subset=["title", "company", "location", "skills"]).sum())
    }
    
    # 2. Drop Duplicates
    df = df_raw.drop_duplicates(subset=["title", "company", "location", "skills"]).copy()
    
    # 3. Standardize Columns
    df["standard_title"] = df["title"].apply(clean_job_title)
    df["clean_experience"] = df["experience"].apply(clean_experience)
    
    # Clean Locations
    df["clean_location"] = df["location"].fillna("Remote").apply(lambda x: str(x).split(",")[0].strip())
    df["clean_location"] = df["clean_location"].apply(lambda x: "Remote" if x == "" else x)
    valid_locations = ["San Francisco", "New York", "Seattle", "Austin", "Boston", "London", "Berlin", "Bengaluru", "Hyderabad", "Toronto", "Remote"]
    df["clean_location"] = df["clean_location"].apply(lambda x: x if x in valid_locations else "Other Tech Hub")
    
    # Clean Remote Status
    def clean_remote_field(row):
        stat = str(row["remote_status"]).strip().lower()
        if stat in ["yes", "true", "1"]:
            return "Yes"
        if stat in ["no", "false", "0"]:
            return "No"
        if row["clean_location"] == "Remote":
            return "Yes"
        return "No"
    df["clean_remote"] = df.apply(clean_remote_field, axis=1)
    
    # 4. Parse Salaries
    parsed = df["salary"].apply(parse_salary)
    df["salary_min"] = [p[0] for p in parsed]
    df["salary_max"] = [p[1] for p in parsed]
    df["salary_avg"] = (df["salary_min"] + df["salary_max"]) / 2
    
    # Outlier Detection (using IQR method on the non-null parsed salaries)
    valid_salaries = df["salary_avg"].dropna()
    Q1 = valid_salaries.quantile(0.25)
    Q3 = valid_salaries.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers_count = int(((df["salary_avg"] < lower_bound) | (df["salary_avg"] > upper_bound)).sum())
    
    # Filter extreme salary errors (e.g. less than 2k or greater than 450k)
    df.loc[(df["salary_avg"] < 2000) | (df["salary_avg"] > 450000), ["salary_min", "salary_max", "salary_avg"]] = np.nan
    
    # Impute missing salaries using Group Mean (Standard Title + Clean Experience)
    group_means = df.groupby(["standard_title", "clean_experience"])["salary_avg"].mean().reset_index()
    group_means.rename(columns={"salary_avg": "imputed_salary"}, inplace=True)
    
    df = df.merge(group_means, on=["standard_title", "clean_experience"], how="left")
    df["salary_avg"] = df["salary_avg"].fillna(df["imputed_salary"]).fillna(24228)
    df["salary_min"] = df["salary_min"].fillna(df["salary_avg"] * 0.85)
    df["salary_max"] = df["salary_max"].fillna(df["salary_avg"] * 1.15)
    df.drop(columns=["imputed_salary"], inplace=True)
    
    # 5. Extract & Clean Skills
    df["skills_list"] = df["skills"].apply(extract_skills)
    
    # Fallback default skills if extraction resulted in empty array
    default_skills = {
        "Software Engineer": ["Python", "Java", "Git", "SQL"],
        "Frontend Developer": ["JavaScript", "React", "HTML5", "CSS3"],
        "Backend Developer": ["Node.js", "Express", "PostgreSQL", "REST APIs"],
        "Data Analyst": ["SQL", "Excel", "Tableau", "Pandas"],
        "Data Scientist": ["Python", "Pandas", "Scikit-Learn", "Machine Learning"],
        "Machine Learning Engineer": ["Python", "PyTorch", "Scikit-Learn", "MLOps"]
    }
    df["skills_list"] = df.apply(lambda r: r["skills_list"] if len(r["skills_list"]) > 0 else default_skills.get(r["standard_title"], ["Python"]), axis=1)
    
    # Join list to string for SQL storage compatibility
    df["clean_skills_str"] = df["skills_list"].apply(lambda x: ", ".join(x))
    
    # Save Cleaned CSV
    df.to_csv(CLEANED_JOBS_PATH, index=False)
    
    # 6. Capture After Metrics
    metrics_after = {
        "total_records": int(len(df)),
        "missing_salaries": int(df["salary_avg"].isna().sum()),
        "missing_locations": int(df["clean_location"].isna().sum()),
        "missing_experience": int((df["clean_experience"] == "Not Specified").sum()),
        "duplicate_records": int(df.duplicated(subset=["title", "company", "clean_location", "clean_skills_str"]).sum()),
        "outliers_filtered": outliers_count
    }
    
    quality_report = {
        "before": metrics_before,
        "after": metrics_after
    }
    
    # Write quality metrics to JSON files (both Datasets and Frontend public data)
    with open(QUALITY_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=4)
        
    with open(os.path.join(FRONTEND_DATA_DIR, "data_quality.json"), "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=4)
        
    print(f"Data cleaning pipeline successfully completed! Quality report written to {QUALITY_JSON_PATH}")

if __name__ == "__main__":
    run_pipeline()
