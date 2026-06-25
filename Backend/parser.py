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
    """Scan text for the presence of master tech skills (case-insensitive keyword matching)."""
    if not text:
        return []
        
    text_lower = text.lower()
    skills_found = []
    
    for skill in ALL_SKILLS:
        # standard word boundaries
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        # special characters check (e.g. C++, Next.js)
        if skill in ["C++", "Next.js", "Node.js", "CI/CD", "A/B Testing", "HTML5", "CSS3"]:
            pattern = re.escape(skill.lower())
            
        if re.search(pattern, text_lower):
            skills_found.append(skill)
            
    return skills_found
