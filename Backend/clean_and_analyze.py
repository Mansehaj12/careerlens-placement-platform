import pandas as pd
import numpy as np
import os
import re
import json
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder

# Paths
RAW_DATA_PATH = "backend/raw_job_postings.csv"
OUTPUT_DIR = "frontend/public/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Master skill list for extraction and matching
ALL_SKILLS = [
    "Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker",
    "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js",
    "Node.js", "Express", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC",
    "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization",
    "R", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "MLOps", "Kubernetes", "AWS",
    "CI/CD", "Terraform", "Linux", "Bash", "Jenkins", "Product Roadmap", "Agile", "User Research",
    "Scrum", "Analytics", "Wireframing", "Network Security", "Penetration Testing", "SIEM", 
    "Cryptography", "Wireshark"
]

def clean_experience(val):
    if pd.isna(val) or str(val).strip() == "":
        return "Not Specified"
    val = str(val).strip().title()
    if val in ["Entry", "Mid", "Senior", "Lead", "Intern", "Not Specified"]:
        return val
    return "Not Specified"

def clean_remote(val):
    if pd.isna(val) or str(val).strip() == "":
        return False
    val_str = str(val).strip().upper()
    if val_str in ["TRUE", "1", "YES"]:
        return True
    return False

def parse_salary(salary_str):
    if pd.isna(salary_str) or str(salary_str).strip() == "":
        return np.nan, np.nan
    
    s = str(salary_str).strip()
    
    # 1. Handle currency adjustments
    multiplier = 1.0
    if "€" in s:
        multiplier = 1.1  # EUR to USD
        s = s.replace("€", "")
    elif "₹" in s:
        multiplier = 0.012  # INR to USD
        s = s.replace("₹", "")
    else:
        s = s.replace("$", "")
        
    s = s.replace(",", "")
    
    # 2. Hourly check
    is_hourly = False
    if "/hr" in s.lower() or "hr" in s.lower() or "hour" in s.lower():
        is_hourly = True
        s = re.sub(r'(?i)/hr|hr|hour|hourly', '', s)
        
    # 3. Year check
    s = re.sub(r'(?i)/yr|yr|year|annual|annually', '', s)
    
    # 4. Extract digits
    # Pattern to find numbers: range (90k - 120k) or single (90k)
    numbers = []
    # Replace 'k' or 'K' with 000
    s_normalized = re.sub(r'(?i)(\d+)k', r'\1000', s)
    
    found = re.findall(r'\d+', s_normalized)
    if not found:
        return np.nan, np.nan
        
    numbers = [float(n) for n in found]
    
    if len(numbers) >= 2:
        val_min, val_max = numbers[0], numbers[1]
    else:
        val_min = val_max = numbers[0]
        
    # Standardize hourly to annual (2080 work hours per year)
    if is_hourly:
        val_min = val_min * 2080
        val_max = val_max * 2080
        
    # Currency conversion
    val_min *= multiplier
    val_max *= multiplier
    
    # Outlier filter (e.g. very low/high salaries that are parsing errors)
    if val_min < 10000 or val_min > 500000:
        return np.nan, np.nan
        
    return val_min, val_max

def extract_skills_from_text(text):
    if pd.isna(text):
        return []
    text_lower = str(text).lower()
    extracted = []
    for skill in ALL_SKILLS:
        # Match word boundaries or clean presence
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        # Special matching for C++, Next.js, CI/CD, A/B Testing, Node.js, .NET etc.
        if skill in ["C++", "Next.js", "Node.js", "CI/CD", "A/B Testing", "HTML5", "CSS3"]:
            pattern = re.escape(skill.lower())
            
        if re.search(pattern, text_lower):
            extracted.append(skill)
    return extracted

def clean_job_title(title):
    # Standardize to one of the 9 roles
    title_lower = str(title).lower()
    roles = {
        "Machine Learning Engineer": ["machine learning", "ml engineer", "ml ops", "mlops"],
        "Data Scientist": ["data scientist", "data science"],
        "Data Analyst": ["data analyst", "analytics analyst", "business analyst"],
        "Frontend Developer": ["frontend", "front-end", "ui developer"],
        "Backend Developer": ["backend", "back-end", "api developer"],
        "DevOps Engineer": ["devops", "site reliability", "sre", "infrastructure"],
        "Cybersecurity Analyst": ["cybersecurity", "security analyst", "pentester", "network security"],
        "Product Manager": ["product manager", "pm"],
        "Software Engineer": ["software engineer", "software developer", "sde", "developer", "programmer"]
    }
    
    for standard_role, keywords in roles.items():
        for kw in keywords:
            if kw in title_lower:
                return standard_role
                
    return "Software Engineer" # Fallback

def main():
    print("Starting Data Cleaning & Analytics Pipeline...")
    
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found at {RAW_DATA_PATH}. Please run generate_raw_data.py first.")
        
    df = pd.read_csv(RAW_DATA_PATH)
    initial_rows = len(df)
    
    # 1. Drop Duplicates
    df.drop_duplicates(subset=["title", "company", "location", "skills", "description"], inplace=True)
    dedup_rows = len(df)
    print(f"Dropped {initial_rows - dedup_rows} duplicate rows.")
    
    # 2. Standardize fields
    df["standard_title"] = df["title"].apply(clean_job_title)
    df["clean_experience"] = df["experience_level"].apply(clean_experience)
    df["clean_remote"] = df["remote"].apply(clean_remote)
    
    # Standardize Location: Extract city (e.g. "San Francisco, CA" -> "San Francisco")
    df["clean_location"] = df["location"].apply(lambda x: str(x).split(",")[0].strip())
    # Group rare locations or misspellings into remote or top hubs
    valid_locations = ["San Francisco", "New York", "Seattle", "Austin", "Boston", "London", "Berlin", "Bengaluru", "Hyderabad", "Toronto"]
    df["clean_location"] = df["clean_location"].apply(lambda x: x if x in valid_locations or x == "Remote" else "Other Tech Hub")
    
    # 3. Clean Salaries
    salaries = df["salary_range"].apply(parse_salary)
    df["salary_min"] = [s[0] for s in salaries]
    df["salary_max"] = [s[1] for s in salaries]
    df["salary_avg"] = (df["salary_min"] + df["salary_max"]) / 2
    
    # Impute missing salaries using Group Mean (Title + Experience Level)
    # Calculate group means
    mean_salaries = df.groupby(["standard_title", "clean_experience"])["salary_avg"].mean().reset_index()
    mean_salaries.rename(columns={"salary_avg": "imputed_salary"}, inplace=True)
    
    # Overall mean for fallback
    global_mean = df["salary_avg"].mean()
    if pd.isna(global_mean):
        global_mean = 95000  # absolute fallback
        
    df = df.merge(mean_salaries, on=["standard_title", "clean_experience"], how="left")
    df["salary_avg"] = df["salary_avg"].fillna(df["imputed_salary"]).fillna(global_mean)
    df["salary_min"] = df["salary_min"].fillna(df["salary_avg"] * 0.85)
    df["salary_max"] = df["salary_max"].fillna(df["salary_avg"] * 1.15)
    df.drop(columns=["imputed_salary"], inplace=True)
    
    print(f"Cleaned and imputed salaries. Global average salary: ${df['salary_avg'].mean():,.2f}")
    
    # 4. Extract Skills
    # Extract clean skill lists from both "skills" column and "description"
    df["skills_extracted"] = df.apply(
        lambda row: list(set(extract_skills_from_text(row["skills"]) + extract_skills_from_text(row["description"]))),
        axis=1
    )
    
    # Ensure every job has at least some skills (fallback to title-specific defaults)
    title_default_skills = {
        "Software Engineer": ["Python", "Git", "SQL"],
        "Frontend Developer": ["JavaScript", "React", "HTML5", "CSS3"],
        "Backend Developer": ["Node.js", "PostgreSQL", "REST APIs"],
        "Data Analyst": ["SQL", "Excel", "Tableau"],
        "Data Scientist": ["Python", "Pandas", "Machine Learning"],
        "Machine Learning Engineer": ["Python", "PyTorch", "Scikit-Learn"],
        "DevOps Engineer": ["AWS", "Docker", "CI/CD"],
        "Product Manager": ["Product Roadmap", "Agile", "Analytics"],
        "Cybersecurity Analyst": ["Network Security", "Linux", "Cryptography"]
    }
    
    def fill_empty_skills(row):
        s = row["skills_extracted"]
        if not s:
            return title_default_skills.get(row["standard_title"], ["Python"])
        return s
        
    df["skills_extracted"] = df.apply(fill_empty_skills, axis=1)
    
    # Save cleaned jobs dataset (sample 200 for user browsing)
    sample_jobs = df.head(200)[["job_id", "title", "standard_title", "company", "salary_min", "salary_max", "salary_avg", "clean_location", "clean_experience", "clean_remote", "skills_extracted"]].to_dict(orient="records")
    
    with open(os.path.join(OUTPUT_DIR, "cleaned_jobs_sample.json"), "w", encoding="utf-8") as f:
        json.dump(sample_jobs, f, indent=2)
        
    # 5. Exploratory Data Analysis & Statistics
    print("Performing statistical calculations...")
    
    # Role Statistics
    role_stats = df.groupby("standard_title").agg(
        avg_salary=("salary_avg", "mean"),
        min_salary=("salary_min", "min"),
        max_salary=("salary_max", "max"),
        job_count=("job_id", "count")
    ).reset_index()
    role_stats["avg_salary"] = role_stats["avg_salary"].round(0)
    role_stats = role_stats.to_dict(orient="records")
    
    # Location Statistics
    loc_stats = df.groupby("clean_location").agg(
        avg_salary=("salary_avg", "mean"),
        job_count=("job_id", "count")
    ).reset_index()
    loc_stats["avg_salary"] = loc_stats["avg_salary"].round(0)
    loc_stats = loc_stats.to_dict(orient="records")
    
    # Experience Level Stats
    exp_stats = df.groupby("clean_experience").agg(
        avg_salary=("salary_avg", "mean"),
        job_count=("job_id", "count")
    ).reset_index()
    exp_stats["avg_salary"] = exp_stats["avg_salary"].round(0)
    # Order exp levels logically
    exp_order = {"Intern": 0, "Entry": 1, "Mid": 2, "Senior": 3, "Lead": 4, "Not Specified": 5}
    exp_stats["order"] = exp_stats["clean_experience"].map(exp_order)
    exp_stats = exp_stats.sort_values("order").drop(columns=["order"]).to_dict(orient="records")
    
    # Remote Work Premium/Trends
    remote_stats = df.groupby("clean_remote").agg(
        avg_salary=("salary_avg", "mean"),
        job_count=("job_id", "count")
    ).reset_index()
    remote_stats["clean_remote"] = remote_stats["clean_remote"].map({True: "Remote", False: "On-site/Hybrid"})
    remote_stats["avg_salary"] = remote_stats["avg_salary"].round(0)
    remote_stats = remote_stats.to_dict(orient="records")
    
    # Skill Demand calculations
    # Flatten list of skills
    all_skills_flat = [skill for sublist in df["skills_extracted"] for skill in sublist]
    skill_counts = pd.Series(all_skills_flat).value_counts().reset_index()
    skill_counts.columns = ["skill", "count"]
    top_skills = skill_counts.head(15).to_dict(orient="records")
    
    # Skill demand by Role
    skills_by_role = {}
    for role in df["standard_title"].unique():
        role_df = df[df["standard_title"] == role]
        flat_skills = [s for sublist in role_df["skills_extracted"] for s in sublist]
        counts = pd.Series(flat_skills).value_counts().head(10).reset_index()
        counts.columns = ["skill", "count"]
        skills_by_role[role] = counts.to_dict(orient="records")
        
    market_stats = {
        "role_stats": role_stats,
        "location_stats": loc_stats,
        "experience_stats": exp_stats,
        "remote_stats": remote_stats,
        "top_skills": top_skills,
        "skills_by_role": skills_by_role,
        "total_jobs": len(df),
        "avg_salary_global": round(df["salary_avg"].mean(), 0),
        "remote_percentage": round((df["clean_remote"].sum() / len(df)) * 100, 1)
    }
    
    with open(os.path.join(OUTPUT_DIR, "market_stats.json"), "w", encoding="utf-8") as f:
        json.dump(market_stats, f, indent=2)
        
    # 6. Train Salary Prediction Model (Ridge Regression)
    print("Training salary prediction model...")
    # Prepare features for ML
    # We want a model like: Salary = Base + coeff(Title) + coeff(Experience) + coeff(Location) + sum(coeff(Skill_i))
    # We will use one-hot encoding for categorical variables, and multi-hot for skills!
    
    # Categorical features
    cat_df = df[["standard_title", "clean_experience", "clean_location"]]
    
    # Skills multi-hot
    skills_dummies = pd.DataFrame(0, index=df.index, columns=ALL_SKILLS)
    for idx, row in df.iterrows():
        skills_dummies.loc[idx, row["skills_extracted"]] = 1
        
    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    cat_encoded = encoder.fit_transform(cat_df)
    cat_feature_names = encoder.get_feature_names_out(["standard_title", "clean_experience", "clean_location"])
    cat_encoded_df = pd.DataFrame(cat_encoded, columns=cat_feature_names, index=df.index)
    
    X = pd.concat([cat_encoded_df, skills_dummies], axis=1)
    y = df["salary_avg"]
    
    # Train Ridge Regression (L2 regularization to avoid extreme coefficients)
    model = Ridge(alpha=1.0)
    model.fit(X, y)
    
    # Export coefficients for frontend calculator
    coefficients = {}
    for feature, coef in zip(X.columns, model.coef_):
        coefficients[feature] = round(coef, 2)
        
    model_export = {
        "intercept": round(model.intercept_, 2),
        "coefficients": coefficients,
        "categories": {
            "titles": list(df["standard_title"].unique()),
            "experience": list(df["clean_experience"].unique()),
            "locations": list(df["clean_location"].unique()),
            "skills": ALL_SKILLS
        }
    }
    
    with open(os.path.join(OUTPUT_DIR, "salary_model.json"), "w", encoding="utf-8") as f:
        json.dump(model_export, f, indent=2)
        
    print("Data cleaning, analytics, and modeling completed successfully!")
    print(f"Data assets exported to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
