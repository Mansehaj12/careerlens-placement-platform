import pypdf
import re

# Master skill list for parsing
ALL_SKILLS = [
    "Python", "Java", "C++", "Go", "System Design", "Git", "SQL", "Docker",
    "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js",
    "Node.js", "Express", "Django", "PostgreSQL", "MongoDB", "Redis", "REST APIs", "gRPC",
    "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "A/B Testing", "Data Visualization",
    "R", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "MLOps", "Kubernetes", "AWS",
    "CI/CD", "Terraform", "Linux", "Bash", "Jenkins", "Product Roadmap", "Agile", "User Research",
    "Scrum", "Analytics", "Wireframing"
]

# Skill category groupings
SKILL_CATEGORIES = {
    "Languages": ["Python", "Java", "C++", "Go", "JavaScript", "TypeScript", "SQL", "R", "Bash"],
    "Frameworks & Web": ["React", "HTML5", "CSS3", "Redux", "Tailwind", "Vite", "Next.js", "Node.js", "Express", "Django", "REST APIs", "gRPC"],
    "Data & ML": ["Pandas", "Scikit-Learn", "TensorFlow", "PyTorch", "Machine Learning", "MLOps", "Statistics", "A/B Testing", "Analytics"],
    "Cloud & DevOps": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform", "Linux", "Jenkins", "Git", "System Design"],
    "Databases & Tools": ["PostgreSQL", "MongoDB", "Redis", "Excel", "Tableau", "Power BI", "Data Visualization"]
}

# Strong action verbs favored by ATS screeners
POWER_ACTION_VERBS = [
    "architected", "engineered", "designed", "implemented", "developed", "built",
    "optimized", "streamlined", "automated", "accelerated", "spearheaded", "deployed",
    "reduced", "increased", "boosted", "integrated", "scaled", "orchestrated", "refactored",
    "launched", "mentored", "created", "configured", "established", "analyzed"
]

WEAK_PHRASES = [
    "worked on", "helped with", "assisted in", "responsible for", "part of team",
    "handled duties", "involved in", "tried to"
]

# Role-specific skill benchmarks reflecting genuine tech industry requirements
ROLE_SKILL_REQUIREMENTS = {
    "Software Engineer": [
        "Python", "Java", "C++", "SQL", "Git", "Docker", "System Design", "Linux", "REST APIs", "CI/CD", "PostgreSQL"
    ],
    "Frontend Developer": [
        "React", "JavaScript", "TypeScript", "HTML5", "CSS3", "Tailwind", "Next.js", "Redux", "Vite", "REST APIs", "Git"
    ],
    "Backend Developer": [
        "Node.js", "PostgreSQL", "REST APIs", "Express", "Redis", "MongoDB", "Django", "SQL", "Docker", "System Design", "Python", "gRPC"
    ],
    "Data Analyst": [
        "SQL", "Python", "Excel", "Tableau", "Power BI", "Pandas", "Statistics", "Data Visualization", "A/B Testing", "Analytics"
    ],
    "Data Scientist": [
        "Python", "Pandas", "Scikit-Learn", "Machine Learning", "SQL", "PyTorch", "TensorFlow", "Statistics", "Data Visualization", "R", "A/B Testing"
    ],
    "Machine Learning Engineer": [
        "Python", "PyTorch", "TensorFlow", "Scikit-Learn", "MLOps", "Docker", "Kubernetes", "AWS", "SQL", "Machine Learning", "CI/CD", "Linux"
    ]
}

# Alias regex patterns for natural resume phrasing
SKILL_PATTERNS = {
    "C++": r'(?:\bc\+\+\b|\bcpp\b)',
    "Next.js": r'(?:\bnext\.?js\b|\bnextjs\b)',
    "Node.js": r'(?:\bnode\.?js\b|\bnodejs\b|\bnode\b)',
    "React": r'(?:\breact\.?js\b|\breactjs\b|\breact\b)',
    "Express": r'(?:\bexpress\.?js\b|\bexpress\b)',
    "PostgreSQL": r'(?:\bpostgresql\b|\bpostgres\b)',
    "MongoDB": r'(?:\bmongodb\b|\bmongo\b)',
    "Kubernetes": r'(?:\bkubernetes\b|\bk8s\b)',
    "Tailwind": r'(?:\btailwind\s*css\b|\btailwind\b)',
    "REST APIs": r'(?:\brest\s*apis?\b|\brestful\b|\bmicroservices\b)',
    "System Design": r'(?:\bsystem\s*design\b|\bdistributed\s*systems\b)',
    "CI/CD": r'(?:\bci\/cd\b|\bgithub\s*actions\b|\bjenkins\b)',
    "HTML5": r'(?:\bhtml5\b|\bhtml\b)',
    "CSS3": r'(?:\bcss3\b|\bcss\b)',
    "A/B Testing": r'(?:\ba\/b\s*testing\b|\bexperimentation\b)',
    "Machine Learning": r'(?:\bmachine\s*learning\b|\bml\b)',
    "Scikit-Learn": r'(?:\bscikit-learn\b|\bsci-kit\b|\bsklearn\b)'
}

def extract_text_from_pdf(file_stream):
    """Extract plain text from an uploaded PDF file stream."""
    try:
        reader = pypdf.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error during PDF text extraction: {e}")
        return ""

def extract_skills_from_text(text):
    """Scan text for the presence of master tech skills with alias support."""
    if not text:
        return []
        
    text_lower = text.lower()
    skills_found = []
    
    for skill in ALL_SKILLS:
        if skill in SKILL_PATTERNS:
            pattern = SKILL_PATTERNS[skill]
        else:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            
        if re.search(pattern, text_lower):
            skills_found.append(skill)
            
    return skills_found

def audit_resume_sections(text):
    """Audit structural presence of core ATS resume sections."""
    text_lower = text.lower()
    
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    has_phone = bool(re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b', text))
    has_links = bool(re.search(r'(?i)(?:github\.com|linkedin\.com|portfolio|gitlab\.com)', text))
    
    contact_detected = has_email and (has_phone or has_links)
    education_detected = bool(re.search(r'(?i)\b(education|academic|bachelor|degree|b\.?tech|m\.?tech|bs|ms|university|college|cgpa|gpa)\b', text_lower))
    experience_detected = bool(re.search(r'(?i)\b(experience|work experience|employment|internship|intern|work history)\b', text_lower))
    projects_detected = bool(re.search(r'(?i)\b(projects|personal projects|portfolio|open source|capstone)\b', text_lower))
    skills_detected = bool(re.search(r'(?i)\b(skills|technical skills|technologies|proficiencies|tech stack)\b', text_lower))
    
    sections = [
        {
            "name": "Contact Information",
            "detected": contact_detected,
            "status": "Present" if contact_detected else "Missing/Incomplete",
            "feedback": "Email & communication links verified" if contact_detected else "Add clear email, phone, and GitHub/LinkedIn links at the header."
        },
        {
            "name": "Education",
            "detected": education_detected,
            "status": "Present" if education_detected else "Missing",
            "feedback": "Degree & academic credentials found" if education_detected else "Include institution name, degree, graduation year, and CGPA."
        },
        {
            "name": "Work / Internships",
            "detected": experience_detected,
            "status": "Present" if experience_detected else "Missing",
            "feedback": "Professional experience section identified" if experience_detected else "Add internship, freelance, or open-source roles with timelines."
        },
        {
            "name": "Technical Projects",
            "detected": projects_detected,
            "status": "Present" if projects_detected else "Missing",
            "feedback": "Hands-on projects section identified" if projects_detected else "Detail at least 2 key projects with architecture summaries."
        },
        {
            "name": "Technical Skills",
            "detected": skills_detected,
            "status": "Present" if skills_detected else "Missing",
            "feedback": "Categorized skill inventory found" if skills_detected else "Organize technical proficiencies into Languages, Frameworks, and Tools."
        }
    ]
    
    detected_count = sum(1 for s in sections if s["detected"])
    section_score = round((detected_count / len(sections)) * 100)
    
    return {
        "sections": sections,
        "detected_count": detected_count,
        "total_sections": len(sections),
        "section_score": section_score
    }

def audit_quantifiable_metrics(text):
    """Detect presence of measurable numbers, metrics, and quantified impact in resume bullet points."""
    metric_pattern = r'(?:\d+(?:\.\d+)?%|\b\d{1,3}(?:,\d{3})+\b|\b\d+\+?\s*(?:k|m|million|lakh|crore)\b|\b\d+\s*(?:ms|seconds|mins|hours|days|weeks|months|years)\b|[\$₹€]\s*\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:k|m|l|lakh|cr))?|\b\d+(?:\.\d+)?x\b)'
    
    matches = list(set(m.strip() for m in re.findall(metric_pattern, text, re.IGNORECASE)))
    count = len(matches)
    
    if count >= 5:
        assessment = "Outstanding"
        score = 100
        tip = "Great job! Your resume effectively communicates quantified business impact."
    elif count >= 3:
        assessment = "Good"
        score = 80
        tip = "Solid metrics present. Try to quantify 1-2 additional project outcomes (e.g. latency reduction, user base)."
    elif count >= 1:
        assessment = "Moderate"
        score = 50
        tip = "Only a few metrics found. Recruiters favor quantified accomplishments over pure task descriptions."
    else:
        assessment = "Needs Improvement"
        score = 25
        tip = "No quantifiable achievements detected. Add numbers (e.g., 'reduced query time by 35%', 'handled 5k users')."
        
    return {
        "metrics_found": matches[:8],
        "count": count,
        "assessment": assessment,
        "score": score,
        "tip": tip
    }

def audit_action_verbs(text):
    """Analyze executive action verb density and identify weak passive phrasing."""
    text_lower = text.lower()
    words = set(re.findall(r'\b[a-zA-Z]+\b', text_lower))
    
    verbs_found = [v.capitalize() for v in POWER_ACTION_VERBS if v in words]
    weak_found = [w for w in WEAK_PHRASES if w in text_lower]
    
    count = len(verbs_found)
    if count >= 6 and len(weak_found) == 0:
        strength = "Strong & Impactful"
        score = 100
    elif count >= 4:
        strength = "Solid"
        score = 80
    elif count >= 2:
        strength = "Moderate"
        score = 60
    else:
        strength = "Weak / Passive"
        score = 35
        
    return {
        "power_verbs": verbs_found[:10],
        "weak_phrases": weak_found,
        "verb_count": count,
        "strength": strength,
        "score": score
    }

def categorize_skills(skills_list):
    """Sort extracted skills into organized domain buckets."""
    categorized = {category: [] for category in SKILL_CATEGORIES}
    uncategorized = []
    
    for skill in skills_list:
        assigned = False
        for category, cat_skills in SKILL_CATEGORIES.items():
            if skill in cat_skills:
                categorized[category].append(skill)
                assigned = True
                break
        if not assigned:
            uncategorized.append(skill)
            
    if uncategorized:
        categorized["Other Tools"] = uncategorized
        
    return {k: v for k, v in categorized.items() if len(v) > 0}

def compute_ats_readiness(skill_match_pct, section_score, impact_score, verb_score):
    """Compute weighted composite ATS score (0-100) and letter grade."""
    # Weights: Domain Skills 55%, Quantifiable Impact 18%, Structural Sections 15%, Action Verbs 12%
    composite = (skill_match_pct * 0.55) + (section_score * 0.15) + (impact_score * 0.18) + (verb_score * 0.12)
    score = round(composite)
    
    if score >= 85:
        grade = "A+"
        verdict = "Exceptional ATS Readiness"
    elif score >= 75:
        grade = "A"
        verdict = "Strong Interview-Ready Profile"
    elif score >= 60:
        grade = "B"
        verdict = "Competitive with Minor Gaps"
    elif score >= 45:
        grade = "C"
        verdict = "Fair — Requires Keyword & Section Tuning"
    else:
        grade = "D"
        verdict = "Substantial ATS Alignment Needed"
        
    return {
        "overall_score": score,
        "grade": grade,
        "verdict": verdict
    }

