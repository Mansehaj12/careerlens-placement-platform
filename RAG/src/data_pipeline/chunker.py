"""
Domain-Aware Section Chunker for CareerLens AI
Splits job descriptions and career documents along semantic boundaries (Sections, Requirements, Responsibilities)
and prepends parent document metadata to every chunk to eliminate context loss.
"""

import re
from typing import List, Dict, Any


class CareerDocChunker:
    """
    Splits career documents into context-preserved chunks.
    Solves the context fragmentation problem by attaching parent headers to every chunk.
    """

    def __init__(self, max_chunk_chars: int = 1200, overlap_chars: int = 150):
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

        # Common structural section markers in job postings & technical documents
        self.section_patterns = [
            r"(?:job\s+description|about\s+the\s+role|role\s+overview|job\s+brief)",
            r"(?:responsibilities|key\s+responsibilities|what\s+you'?ll\s+do|duties)",
            r"(?:requirements|qualifications|what\s+we'?re\s+looking\s+for|skills\s+required|must\s+have)",
            r"(?:nice\s+to\s+have|preferred\s+qualifications|good\s+to\s+have)",
            r"(?:education|eligibility|academic\s+criteria)",
            r"(?:compensation|salary|perks|benefits|what\s+we\s+offer)",
            r"(?:about\s+the\s+company|about\s+us|who\s+we\s+are)",
        ]

    def _split_into_sections(self, text: str) -> List[Dict[str, str]]:
        """Splits document text by structural section headings if present."""
        combined_pattern = f"(\n(?:{'|'.join(self.section_patterns)})[:\n])"
        parts = re.split(combined_pattern, text, flags=re.IGNORECASE)

        if len(parts) <= 1:
            # No recognized section headers; treat whole text as general body
            return [{"header": "General Details", "content": text}]

        sections = []
        current_header = "Overview"
        current_body = parts[0].strip()

        if current_body:
            sections.append({"header": current_header, "content": current_body})

        for i in range(1, len(parts), 2):
            header = parts[i].strip().replace("\n", "").replace(":", "")
            content = parts[i + 1].strip() if (i + 1) < len(parts) else ""
            if content:
                sections.append({"header": header, "content": content})

        return sections

    def _recursive_paragraph_split(self, text: str) -> List[str]:
        """Splits long section text by paragraphs, then sentences with sliding overlap."""
        if len(text) <= self.max_chunk_chars:
            return [text]

        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.max_chunk_chars:
                current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # If a single paragraph is larger than max_chunk_chars, split by sentence
                if len(para) > self.max_chunk_chars:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    sub_chunk = ""
                    for sent in sentences:
                        if len(sub_chunk) + len(sent) + 1 <= self.max_chunk_chars:
                            sub_chunk = f"{sub_chunk} {sent}" if sub_chunk else sent
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk)
                            sub_chunk = sent
                    if sub_chunk:
                        current_chunk = sub_chunk
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def chunk_job_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a cleaned job document dictionary and returns a list of enriched chunk objects.
        Each chunk includes metadata and a contextual prefix.
        """
        doc_id = doc.get("id", "doc_unknown")
        title = doc.get("title", "Unknown Role")
        company = doc.get("company", "Confidential")
        category = doc.get("category", "General Tech")
        location = doc.get("location", "Not Specified")
        exp_min = doc.get("min_exp")
        exp_max = doc.get("max_exp")
        exp_str = f"{exp_min}-{exp_max} yrs" if exp_min is not None else "Experience Not Specified"
        skills = doc.get("skills", "")
        raw_text = doc.get("description", "")

        # Create contextual metadata prefix
        context_prefix = (
            f"[ROLE: {title} | COMPANY: {company} | DOMAIN: {category} | "
            f"EXP: {exp_str} | LOCATION: {location} | KEY_SKILLS: {skills}]\n"
        )

        sections = self._split_into_sections(raw_text)
        enriched_chunks = []

        chunk_idx = 0
        for sec in sections:
            header = sec["header"]
            body = sec["content"]
            sub_chunks = self._recursive_paragraph_split(body)

            for sub_text in sub_chunks:
                chunk_id = f"{doc_id}_c{chunk_idx}"
                full_content = f"{context_prefix}SECTION: {header}\n{sub_text}"

                enriched_chunks.append({
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "title": title,
                    "company": company,
                    "category": category,
                    "location": location,
                    "min_exp": exp_min if exp_min is not None else -1.0,
                    "max_exp": exp_max if exp_max is not None else -1.0,
                    "skills": skills,
                    "section": header,
                    "text": full_content,
                    "raw_section_text": sub_text
                })
                chunk_idx += 1

        return enriched_chunks
