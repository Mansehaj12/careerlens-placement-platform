"""
Document Cleaning & Preprocessing Pipeline for CareerLens AI
Cleans raw text, strips HTML, fixes unicode corruption, and extracts structured metadata.
"""

import re
import html
from typing import Dict, Any, Optional, Tuple


class TextCleaner:
    """Production-grade text sanitizer for job descriptions, resumes, and technical docs."""

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        if not text or not isinstance(text, str):
            return ""

        # Decode HTML entities (e.g., &amp; -> &, &lt; -> <)
        text = html.unescape(text)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)

        # Replace unicode replacement characters and artifacts (common in scraped Naukri data)
        text = text.replace("\ufffd", " ").replace("", " ")
        text = text.replace("\xa0", " ").replace("\t", " ")

        # Normalize bullet points and dashes
        text = re.sub(r"[•●▪■►▶✓✔–—−]", "- ", text)
        text = re.sub(r"==\s*>", "->", text)

        # Remove multiple consecutive blank lines or excessive spaces
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        return text.strip()

    @staticmethod
    def parse_experience(exp_str: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
        """Parses experience strings like '3 - 7 yrs', '2-5 Yrs', '5 yrs', 'Freshers' into (min_exp, max_exp)."""
        if not exp_str or not isinstance(exp_str, str):
            return None, None

        exp_clean = exp_str.lower().strip()
        if "fresher" in exp_clean or "0-" in exp_clean or "0 -" in exp_clean:
            return 0.0, 1.0

        # Match range pattern like '3 - 8' or '3-8'
        range_match = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", exp_clean)
        if range_match:
            try:
                return float(range_match.group(1)), float(range_match.group(2))
            except ValueError:
                pass

        # Match single number like '5+ yrs' or '3 yrs'
        single_match = re.search(r"(\d+(?:\.\d+)?)", exp_clean)
        if single_match:
            try:
                val = float(single_match.group(1))
                return val, val
            except ValueError:
                pass

        return None, None

    @staticmethod
    def categorize_role(title: str, skills: str) -> str:
        """Assigns broad tech category for metadata pre-filtering."""
        combined = f"{title} {skills}".lower()

        if any(k in combined for k in ["data sci", "machine learning", "deep learning", "ai ", "nlp", "computer vision", "llm", "genai", "pytorch"]):
            return "Data Science & AI"
        elif any(k in combined for k in ["data eng", "etl", "spark", "hadoop", "databricks", "data warehouse", "snowflake"]):
            return "Data Engineering"
        elif any(k in combined for k in ["data anal", "business anal", "power bi", "tableau", "bi developer", "sql anal"]):
            return "Data Analytics & BI"
        elif any(k in combined for k in ["devops", "cloud", "aws", "azure", "gcp", "kubernetes", "docker", "ci/cd", "sre", "site reliability"]):
            return "DevOps & Cloud"
        elif any(k in combined for k in ["react", "frontend", "front end", "angular", "vue", "ui/ux", "web designer", "javascript"]):
            return "Frontend Development"
        elif any(k in combined for k in ["backend", "back end", "node", "django", "fastapi", "spring boot", "golang", "java developer", "python developer", "c#", ".net"]):
            return "Backend & Software Engineering"
        elif any(k in combined for k in ["full stack", "fullstack", "mern", "mean"]):
            return "Full Stack Development"
        elif any(k in combined for k in ["qa", "testing", "automation test", "selenium", "sdet"]):
            return "QA & Testing"
        else:
            return "General Tech"
