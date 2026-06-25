import csv
import random
import os
import urllib.request
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

os.makedirs("Datasets", exist_ok=True)

companies_list = [
    "TCS", "Infosys", "Wipro", "Cognizant", "Zoho", "Flipkart", "Swiggy", "Zomato",
    "Paytm", "HCLTech", "Tech Mahindra", "Ola", "Freshworks", "L&T Infotech", "Mindtree",
    "Accenture India", "Capgemini India", "Cred", "PhonePe", "Razorpay", "BrowserStack"
]

roles_skills = {
    "Software Engineer": ["Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker"],
    "Frontend Developer": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js"],
    "Backend Developer": ["Node.js", "Express", "Python", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC"],
    "Data Analyst": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization"],
    "Data Scientist": ["Python", "R", "SQL", "Pandas", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "Statistics"],
    "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "MLOps", "SQL", "Docker", "Kubernetes", "AWS"]
}

locations = [
    "Bengaluru", "Hyderabad", "Mumbai", "Pune", "Chennai", "Delhi NCR", "Noida", "Gurgaon", "Remote"
]

industries = ["IT Services", "Software Products", "E-commerce", "Fintech", "Consulting", "Healthtech", "Logistics"]
employment_types = ["Full-time", "Part-time", "Contract", "Internship"]

def download_naukri_dataset():
    dest = "Datasets/naukri_raw.csv"
    if os.path.exists(dest):
        print(f"Real Naukri dataset already exists at {dest}. Skipping download.")
        return dest
    
    urls = [
        "https://huggingface.co/datasets/jason1966/PromptCloudHQ_jobs-on-naukricom/resolve/main/naukri_com-job_sample.csv",
        "https://raw.githubusercontent.com/mrmaheshrajput/edanaukri/master/naukri_com-job_sample.csv"
    ]
    
    for url in urls:
        print(f"Attempting to download real Naukri.com dataset from: {url}")
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
                out_file.write(response.read())
            print("Successfully downloaded real Naukri.com dataset!")
            return dest
        except Exception as e:
            print(f"Failed to download from this URL: {e}")
            
    print("All URLs failed. Falling back to standard synthetic generator.")
    return None

# Mappers for real Naukri columns
def map_naukri_title(t):
    t_lower = str(t).lower()
    if "machine learning" in t_lower or "ml" in t_lower:
        return "Machine Learning Engineer"
    elif "data scientist" in t_lower or "science" in t_lower:
        return "Data Scientist"
    elif "data analyst" in t_lower or "analytics" in t_lower:
        return "Data Analyst"
    elif "frontend" in t_lower or "ui" in t_lower or ("front" in t_lower and "end" in t_lower):
        return "Frontend Developer"
    elif "backend" in t_lower or "api" in t_lower or ("back" in t_lower and "end" in t_lower):
        return "Backend Developer"
    else:
        return "Software Engineer"

def map_naukri_location(loc):
    if pd.isna(loc):
        return "Bengaluru"
    loc_lower = str(loc).lower()
    if "bangalore" in loc_lower or "bengaluru" in loc_lower:
        return "Bengaluru"
    elif "hyderabad" in loc_lower:
        return "Hyderabad"
    elif "remote" in loc_lower or "work from home" in loc_lower:
        return "Remote"
    elif any(x in loc_lower for x in ["mumbai", "pune", "chennai", "delhi", "noida", "gurgaon"]):
        return "Other Tech Hub"
    return "Other Tech Hub"

def map_naukri_salary(payrate):
    if pd.isna(payrate) or str(payrate).strip() == "" or "not disclosed" in str(payrate).lower():
        return ""
    
    # Payrate in lakhs per annum like "8,00,000 - 15,00,000 P.A." or "8 - 15 Lakhs P.A."
    s = str(payrate).replace(",", "").replace("P.A.", "").replace("P.a.", "").strip()
    found = re.findall(r'\d+', s)
    if len(found) >= 2:
        min_val = float(found[0])
        max_val = float(found[1])
        if min_val < 100:
            min_val *= 100000
        if max_val < 100:
            max_val *= 100000
        # Convert INR to USD (multiplied by 0.012)
        min_usd = int(min_val * 0.012)
        max_usd = int(max_val * 0.012)
        if min_usd > 1000 and max_usd < 300000:
            return f"${min_usd:,} - ${max_usd:,}"
    return ""

def map_naukri_experience(exp):
    if pd.isna(exp):
        return "Mid"
    s = str(exp).lower()
    found = re.findall(r'\d+', s)
    if found:
        min_yrs = int(found[0])
        if min_yrs <= 1:
            return "Entry"
        elif min_yrs <= 4:
            return "Mid"
        elif min_yrs <= 8:
            return "Senior"
        else:
            return "Lead"
    return "Mid"

def generate_messy_salary(role, exp):
    # Standard Indian salaries in USD equivalent (1 USD = 83.33 INR)
    # E.g. Software Engineer: 6 LPA to 25 LPA (approx $7,200 to $30,000)
    base_salaries = {
        "Software Engineer": (7200, 30000),
        "Frontend Developer": (5400, 24000),
        "Backend Developer": (6000, 26400),
        "Data Analyst": (4800, 18000),
        "Data Scientist": (7200, 33600),
        "Machine Learning Engineer": (8400, 38400)
    }
    min_val, max_val = base_salaries[role]
    multiplier = {"Intern": 0.4, "Entry": 0.8, "Mid": 1.0, "Senior": 1.3, "Lead": 1.5, "Not Specified": 0.95}[exp]
    min_val = int(min_val * multiplier)
    max_val = int(max_val * multiplier)
    
    fmt = random.choice(["range_long", "range_k", "single_long", "hourly", "empty", "inconsistent_currency"])
    if fmt == "range_long":
        return f"${min_val:,} - ${max_val:,}"
    elif fmt == "range_k":
        return f"${min_val//1000}k - ${max_val//1000}k"
    elif fmt == "single_long":
        return f"${random.randint(min_val, max_val):,}/yr"
    elif fmt == "hourly":
        return f"${random.randint(5, 25)}/hr"
    elif fmt == "empty":
        return ""
    else:
        if random.random() > 0.5:
            return f"€{int(min_val * 0.9):,} - €{int(max_val * 0.9):,}"
        else:
            return f"₹{int(min_val * 80):,} - ₹{int(max_val * 80):,}"

def generate_messy_skills(skills_list):
    all_generic = ["Communication", "Teamwork", "Agile", "Excel", "Problem Solving"]
    chosen = random.sample(skills_list, k=random.randint(3, min(6, len(skills_list))))
    chosen += random.sample(all_generic, k=random.randint(0, 2))
    
    fmt = random.choice(["comma", "pipe", "semicolon", "text_mix"])
    if fmt == "comma":
        return ", ".join(chosen)
    elif fmt == "pipe":
        return "|".join(chosen)
    elif fmt == "semicolon":
        return "; ".join(chosen)
    else:
        return f"Required: {', '.join(chosen)}. Key technical proficiency."

def main():
    raw_file = download_naukri_dataset()
    num_records = 52000
    start_date = datetime.now() - timedelta(days=120)
    data = []
    
    if raw_file and os.path.exists(raw_file):
        try:
            # Read chunks or whole file safely (52 MB is large, so pandas handles it efficiently)
            df_naukri = pd.read_csv(raw_file)
            print(f"Loaded {len(df_naukri)} real Naukri job postings. Bootstrapping to {num_records} rows...")
            
            # Extract lists of real values
            real_companies = df_naukri["company"].dropna().tolist()
            real_payrates = df_naukri["payrate"].dropna().tolist()
            real_locations = df_naukri["joblocation_address"].dropna().tolist()
            real_exps = df_naukri["experience"].dropna().tolist()
            
            for i in range(1, num_records + 1):
                # 65% chance to draw from Naukri real dataset distribution
                if random.random() < 0.65 and len(df_naukri) > 0:
                    real_row = df_naukri.sample(n=1).iloc[0]
                    role = map_naukri_title(real_row["jobtitle"])
                    
                    # Company
                    comp = str(real_row["company"]).strip()
                    if pd.isna(real_row["company"]) or not comp or comp.lower() in ["nan", "none"]:
                        comp = random.choice(companies_list)
                        
                    # Location
                    loc = map_naukri_location(real_row["joblocation_address"])
                    
                    # Salary (INR Converted to USD)
                    salary_str = map_naukri_salary(real_row["payrate"])
                    if not salary_str:
                        salary_str = generate_messy_salary(role, "Mid")
                        
                    # Experience
                    exp = map_naukri_experience(real_row["experience"])
                    
                    # Skills (use real ones or fall back)
                    skills = str(real_row["skills"]).strip()
                    if pd.isna(real_row["skills"]) or not skills or skills.lower() in ["nan", "none"]:
                        skills = generate_messy_skills(roles_skills[role])
                else:
                    # pure simulation fallback to balance tech roles
                    role = random.choice(list(roles_skills.keys()))
                    comp = random.choice(companies_list)
                    loc = random.choice(["Bengaluru", "Hyderabad", "Remote", "Other Tech Hub"])
                    exp = random.choice(["Entry", "Mid", "Senior", "Lead", "Intern"])
                    salary_str = generate_messy_salary(role, exp)
                    skills = generate_messy_skills(roles_skills[role])
                    
                ind = random.choice(industries)
                emp_type = random.choice(employment_types)
                post_date = (start_date + timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d")
                
                job_record = {
                    "title": role if random.random() > 0.1 else f"{exp} {role}",
                    "company": comp,
                    "location": loc if random.random() > 0.05 else "",
                    "salary": salary_str,
                    "experience": exp if random.random() > 0.08 else "",
                    "skills": skills,
                    "industry": ind,
                    "employment_type": emp_type,
                    "remote_status": "Yes" if loc == "Remote" or random.random() < 0.2 else "No",
                    "posting_date": post_date
                }
                data.append(job_record)
                
            print("Successfully bootstrapped dataset from real-world Indian company hiring metrics!")
        except Exception as ex:
            print(f"Error parsing Naukri dataset: {ex}. Falling back to standard synthetic generator.")
            raw_file = None
            
    if not raw_file:
        print("Generating pure synthetic dataset...")
        for i in range(1, num_records + 1):
            role = random.choice(list(roles_skills.keys()))
            company = random.choice(companies_list)
            exp = random.choice(["Entry", "Mid", "Senior", "Lead", "Intern", "Not Specified"])
            loc = random.choice(["Bengaluru", "Hyderabad", "Remote", "Other Tech Hub"])
            ind = random.choice(industries)
            emp_type = random.choice(employment_types)
            
            salary = generate_messy_salary(role, exp)
            skills = generate_messy_skills(roles_skills[role])
            remote_val = "Yes" if loc == "Remote" or random.random() < 0.2 else "No"
            post_date = (start_date + timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d")
            
            job_record = {
                "title": role if random.random() > 0.1 else f"{exp} {role}",
                "company": company,
                "location": loc if random.random() > 0.05 else "",
                "salary": salary,
                "experience": exp if random.random() > 0.08 else "",
                "skills": skills,
                "industry": ind,
                "employment_type": emp_type,
                "remote_status": remote_val if random.random() > 0.1 else "",
                "posting_date": post_date
            }
            data.append(job_record)
            
    csv_file = "Datasets/raw_jobs.csv"
    fields = ["title", "company", "location", "salary", "experience", "skills", "industry", "employment_type", "remote_status", "posting_date"]
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
        
    print(f"Dataset generated with {len(data)} records in {csv_file}")
    generate_students_dataset(5000)

def generate_students_dataset(num_records=5000):
    data = []
    for i in range(1, num_records + 1):
        cgpa = round(random.uniform(5.5, 10.0), 2)
        internships = random.choice([0, 0, 0, 1, 1, 2, 3])
        projects = random.choice([0, 1, 1, 2, 2, 3, 4, 5])
        certifications = random.choice([0, 0, 1, 1, 2, 3])
        skills_count = random.randint(3, 15)
        
        logit = -7.5 + (0.95 * cgpa) + (1.6 * internships) + (0.75 * projects) + (0.5 * certifications) + (0.1 * skills_count)
        prob = 1 / (1 + np.exp(-logit))
        placed = 1 if random.random() < prob else 0
        
        data.append({
            "student_id": f"STU_{i:04d}",
            "cgpa": cgpa,
            "skills_count": skills_count,
            "internships": internships,
            "projects": projects,
            "certifications": certifications,
            "placed": placed
        })
        
    csv_file = "Datasets/student_profiles.csv"
    fields = ["student_id", "cgpa", "skills_count", "internships", "projects", "certifications", "placed"]
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
        
    print(f"Generated {len(data)} student academic profiles in Datasets/student_profiles.csv")

if __name__ == "__main__":
    main()
