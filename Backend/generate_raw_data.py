import csv
import random
import os
from datetime import datetime, timedelta

# Create backend directory if it doesn't exist
os.makedirs("backend", exist_ok=True)

# Domain data for simulation
companies = [
    "Google", "Microsoft", "Meta", "Amazon", "Apple", "Netflix", "Uber", "Stripe", "Airbnb", "Spotify",
    "Salesforce", "Atlassian", "HubSpot", "Shopify", "Databricks", "Snowflake", "Zoom", "Slack", "Adobe", "Figma",
    "ByteDance", "Tencent", "Infosys", "TCS", "Wipro", "Cognizant", "Accenture", "Capgemini", "PayPal",
    "Coinbase", "Robinhood", "Plaid", "Chime", "Nvidia", "Intel", "AMD", "Qualcomm", "Tesla", "SpaceX"
]

roles_skills = {
    "Software Engineer": ["Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker"],
    "Frontend Developer": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js"],
    "Backend Developer": ["Node.js", "Express", "Python", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC"],
    "Data Analyst": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization"],
    "Data Scientist": ["Python", "R", "SQL", "Pandas", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "Statistics"],
    "Machine Learning Engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "MLOps", "SQL", "Docker", "Kubernetes", "AWS"],
    "DevOps Engineer": ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform", "Linux", "Bash", "Jenkins", "Git"],
    "Product Manager": ["Product Roadmap", "Agile", "User Research", "Scrum", "SQL", "Analytics", "A/B Testing", "Wireframing"],
    "Cybersecurity Analyst": ["Network Security", "Penetration Testing", "Linux", "SIEM", "Cryptography", "Python", "Wireshark"]
}

locations = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "Boston, MA",
    "London, UK", "Berlin, Germany", "Bengaluru, India", "Hyderabad, India", "Toronto, Canada",
    "Remote", "Remote, US", "Remote, UK", "Remote, India"
]

experience_levels = ["Entry", "Mid", "Senior", "Lead", "Intern", "Not Specified"]

descriptions_templates = {
    "Software Engineer": "We are seeking a talented Software Engineer to join our core engineering team. You will design, develop, and maintain high-performance scalable systems. Ideal candidates have strong experience in programming and system design.",
    "Frontend Developer": "Looking for a Frontend Developer passionate about building gorgeous, responsive user interfaces. You will collaborate closely with UI/UX designers to bring ideas to life. Experience with modern JS frameworks is a must.",
    "Backend Developer": "Join us as a Backend Developer to build scalable APIs, database architectures, and microservices. You will optimize system performance and ensure data security across all integrations.",
    "Data Analyst": "We need a Data Analyst to translate complex datasets into actionable business insights. You will create reports, design dashboards, and perform exploratory data analysis to drive executive decisions.",
    "Data Scientist": "We are hiring a Data Scientist to build predictive models and run advanced statistical analyses. You will mine large data structures to uncover hidden trends and implement machine learning solutions.",
    "Machine Learning Engineer": "Looking for an ML Engineer to deploy machine learning models in production environments. You will optimize inference speed, design MLOps pipelines, and scale training workloads.",
    "DevOps Engineer": "Join our cloud infrastructure team to automate pipelines, manage containerized applications, and improve system reliability. Experience with infrastructure-as-code is highly valued.",
    "Product Manager": "Seeking a Product Manager to own product features from concept to launch. You will write specs, coordinate with design and engineering, and define product roadmaps based on customer data.",
    "Cybersecurity Analyst": "We are looking for a Cybersecurity Analyst to monitor systems, conduct penetration tests, and secure our cloud infrastructure. You will respond to security incidents and audit system logs."
}

def generate_messy_salary(role, exp):
    # Base salary ranges
    base_salaries = {
        "Software Engineer": (80000, 160000),
        "Frontend Developer": (70000, 140000),
        "Backend Developer": (75000, 150000),
        "Data Analyst": (60000, 110000),
        "Data Scientist": (85000, 170000),
        "Machine Learning Engineer": (95000, 190000),
        "DevOps Engineer": (80000, 160000),
        "Product Manager": (90000, 170000),
        "Cybersecurity Analyst": (75000, 140000)
    }
    
    min_val, max_val = base_salaries[role]
    
    # Adjust for experience
    multiplier = {
        "Intern": 0.4,
        "Entry": 0.8,
        "Mid": 1.0,
        "Senior": 1.3,
        "Lead": 1.5,
        "Not Specified": 0.95
    }[exp]
    
    min_val = int(min_val * multiplier)
    max_val = int(max_val * multiplier)
    
    # Randomly select a format to represent messy data
    format_type = random.choice([
        "range_long", "range_k", "single_long", "single_k", 
        "hourly", "empty", "text_only", "inconsistent_currency"
    ])
    
    if format_type == "range_long":
        return f"${min_val:,} - ${max_val:,}"
    elif format_type == "range_k":
        return f"${min_val//1000}k - ${max_val//1000}k"
    elif format_type == "single_long":
        return f"${random.randint(min_val, max_val):,}/yr"
    elif format_type == "single_k":
        return f"${random.randint(min_val, max_val)//1000}K"
    elif format_type == "hourly":
        # Simulate hourly pay for interns/entry level
        hourly = random.randint(30, 85)
        return f"${hourly}/hr"
    elif format_type == "empty":
        return ""
    elif format_type == "text_only":
        return "Competitive salary based on experience"
    elif format_type == "inconsistent_currency":
        # European currency or local rupee simulation
        if random.random() > 0.5:
            return f"€{int(min_val * 0.9):,} - €{int(max_val * 0.9):,}"
        else:
            return f"₹{int(min_val * 80):,} - ₹{int(max_val * 80):,}"

def generate_messy_skills(skills_list):
    # Mix some random generic skills
    all_generic = ["Communication", "Teamwork", "Problem Solving", "Agile", "Microsoft Office", "Jira", "Slack"]
    
    # Choose 3-6 skills from domain list
    chosen = random.sample(skills_list, k=random.randint(3, min(6, len(skills_list))))
    # Mix 1-2 generic skills
    chosen += random.sample(all_generic, k=random.randint(0, 2))
    
    # Format dynamically
    fmt = random.choice(["comma", "pipe", "semicolon", "json_string", "text_mix"])
    if fmt == "comma":
        return ", ".join(chosen)
    elif fmt == "pipe":
        return "|".join(chosen)
    elif fmt == "semicolon":
        return "; ".join(chosen)
    elif fmt == "json_string":
        return str(chosen)
    elif fmt == "text_mix":
        return f"Proficiency in: {', '.join(chosen)}. Knowledge of other modern tech stacks is a plus."

def generate_data(num_records=8000):
    start_date = datetime.now() - timedelta(days=90)
    data = []
    
    # Keep track of generated jobs to insert exact duplicates (approx 5%)
    generated_pool = []
    
    for job_id in range(1, num_records + 1):
        # 5% chance to duplicate an existing job from pool
        if generated_pool and random.random() < 0.05:
            dup_job = random.choice(generated_pool).copy()
            # Change ID to look like a separate entry
            dup_job["job_id"] = f"JOB_{job_id:05d}"
            # Slightly change date
            days_offset = random.randint(1, 5)
            dup_date = datetime.strptime(dup_job["posting_date"], "%Y-%m-%d") + timedelta(days=days_offset)
            dup_job["posting_date"] = dup_date.strftime("%Y-%m-%d")
            data.append(dup_job)
            continue
            
        role = random.choice(list(roles_skills.keys()))
        company = random.choice(companies)
        exp = random.choice(experience_levels)
        loc = random.choice(locations)
        
        salary = generate_messy_salary(role, exp)
        skills = generate_messy_skills(roles_skills[role])
        desc = descriptions_templates[role]
        
        # Inconsistent remote field
        remote_val = random.choice([True, False, None])
        if remote_val is None:
            remote_field = ""
        else:
            remote_field = random.choice(["Yes", "No", "1", "0", "TRUE", "FALSE"]) if random.random() > 0.3 else str(remote_val)
            
        post_date = (start_date + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")
        
        # Format the experience field inconsistently
        exp_val = exp if random.random() > 0.2 else exp.lower()
        if exp_val == "not specified" and random.random() > 0.5:
            exp_val = "" # missing experience level
            
        job_record = {
            "job_id": f"JOB_{job_id:05d}",
            "title": role if random.random() > 0.15 else f"{exp} {role}", # Inconsistent titles
            "company": company,
            "salary_range": salary,
            "location": loc if random.random() > 0.1 else loc.split(",")[0], # Inconsistent city/state formats
            "experience_level": exp_val,
            "skills": skills,
            "description": desc,
            "remote": remote_field,
            "posting_date": post_date
        }
        
        data.append(job_record)
        
        # Add to duplication pool (max pool size 100)
        if len(generated_pool) < 100:
            generated_pool.append(job_record)
        else:
            if random.random() > 0.5:
                generated_pool[random.randint(0, 99)] = job_record
                
    # Shuffle list
    random.shuffle(data)
    
    # Write to CSV
    csv_file_path = os.path.join("backend", "raw_job_postings.csv")
    fields = ["job_id", "title", "company", "salary_range", "location", "experience_level", "skills", "description", "remote", "posting_date"]
    
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
        
    print(f"Successfully generated {len(data)} job listings in {csv_file_path}")

if __name__ == "__main__":
    generate_data(8000)
