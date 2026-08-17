import os
import re
from typing import Optional, Dict, Any, List
import spacy

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

from models.candidate import Candidate
from services.text_processor import (
    clean_text,
    extract_skills_from_text,
    extract_certifications_from_text,
    extract_education_from_text,
    parse_experience_years
)

# Load lightweight spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None


class ResumeParser:
    """Parses resumes in PDF, DOCX, and TXT formats and extracts candidate profiles."""

    @staticmethod
    def extract_text_from_pdf(filepath: str) -> str:
        """Extract text using pdfplumber with PyPDF2 fallback."""
        text = ""
        # Try pdfplumber first (high fidelity)
        if pdfplumber:
            try:
                with pdfplumber.open(filepath) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                if text.strip():
                    return text
            except Exception:
                pass

        # Fallback to PyPDF2
        if PyPDF2:
            try:
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                if text.strip():
                    return text
            except Exception:
                pass

        return text

    @staticmethod
    def extract_text_from_docx(filepath: str) -> str:
        """Extract text from .docx document."""
        if not docx:
            return ""
        try:
            doc = docx.Document(filepath)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        full_text.append(" | ".join(row_text))
            return "\n".join(full_text)
        except Exception:
            return ""

    @staticmethod
    def extract_text_from_txt(filepath: str) -> str:
        """Extract text from plain text file with multi-encoding fallback."""
        for enc in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    return f.read()
            except Exception:
                continue
        return ""

    @classmethod
    def extract_raw_text(cls, filepath: str) -> str:
        """Dispatcher for extracting text based on file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".pdf":
            return cls.extract_text_from_pdf(filepath)
        elif ext in [".docx", ".doc"]:
            return cls.extract_text_from_docx(filepath)
        elif ext == ".txt":
            return cls.extract_text_from_txt(filepath)
        return ""

    @staticmethod
    def extract_email(text: str) -> str:
        """Extract primary email address from text."""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        if matches:
            # Return the first valid email
            return matches[0].strip()
        return "Not detected"

    @staticmethod
    def extract_phone(text: str) -> str:
        """Extract contact phone number in various formats."""
        phone_patterns = [
            r'(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',   # US / General (+1 123-456-7890)
            r'(?:\+?91[\s-]?)?[6789]\d{9}',                                  # India (+91 9876543210)
            r'\+?\d{2,3}[\s-]?\d{4}[\s-]?\d{4,6}',                           # International
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                digits = re.sub(r'\D', '', m)
                if 10 <= len(digits) <= 14:
                    return m.strip()
        return "Not detected"

    @staticmethod
    def extract_name(text: str, email: str = "") -> str:
        """
        Extract candidate name using top header heuristics, email correlation,
        and spaCy NER.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        ignored_keywords = {
            "resume", "curriculum vitae", "cv", "page 1", "page 2", "profile", 
            "contact", "phone", "email", "education", "experience", "skills",
            "summary", "about me", "portfolio", "linkedin", "github", "technical skills",
            "professional summary", "work experience", "certifications", "projects",
            "developer", "engineer", "specialist", "architect", "lead", "senior", "junior",
            "problem solving", "linux", "python", "java", "react", "docker"
        }

        # 1. Check top 3 lines: typically the candidate's full name is line 0 or 1
        for line in lines[:4]:
            clean_line = re.sub(r'[,|•·\(\)]', '', line).strip()
            words = clean_line.split()
            if 2 <= len(words) <= 4:
                # Check if all words are letters/periods/hyphens and not ignored keywords
                if all(w.replace(".", "").replace("-", "").isalpha() for w in words):
                    if not any(w.lower() in ignored_keywords for w in words):
                        if not re.search(r'@|\.com|http|\+?\d{6,}', clean_line):
                            return clean_line.title()

        # 2. Email fallback (e.g. rahul.sharma@example.com -> Rahul Sharma)
        if email and email != "Not detected":
            local_part = email.split("@")[0]
            name_parts = re.split(r'[._-]', local_part)
            clean_parts = [p.title() for p in name_parts if p.isalpha() and len(p) > 1 and p.lower() not in ignored_keywords]
            if len(clean_parts) >= 2:
                return " ".join(clean_parts)

        # 3. spaCy NER on top text block
        if nlp:
            top_block = "\n".join(lines[:6])
            doc = nlp(top_block)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    clean_ent = ent.text.strip()
                    words = clean_ent.split()
                    if 2 <= len(words) <= 4:
                        if not any(w.lower() in ignored_keywords for w in words):
                            if not re.search(r'\d|@|\.com', clean_ent):
                                return clean_ent.title()

        # 4. Single-name fallback if email has at least one valid part
        if email and email != "Not detected":
            local_part = email.split("@")[0]
            name_parts = re.split(r'[._-]', local_part)
            clean_parts = [p.title() for p in name_parts if p.isalpha() and len(p) > 1 and p.lower() not in ignored_keywords]
            if clean_parts:
                return " ".join(clean_parts)

        return "Not detected"

    @staticmethod
    def extract_location(text: str) -> str:
        """Extract candidate location/city from resume."""
        if nlp:
            # Check top 15 lines where contact info resides
            top_lines = "\n".join([line.strip() for line in text.split("\n")[:15] if line.strip()])
            doc = nlp(top_lines)
            for ent in doc.ents:
                if ent.label_ in ("GPE", "LOC"):
                    loc = ent.text.strip()
                    if len(loc) > 2 and not re.search(r'\d', loc):
                        return loc.title()

        # Common city/region fallback patterns
        loc_match = re.search(r'(?:Location|Address|City):\s*([A-Za-z\s,]+)', text, re.IGNORECASE)
        if loc_match:
            return loc_match.group(1).strip().title()

        return "Not detected"

    @classmethod
    def parse_resume(cls, filepath: str, original_filename: str = "") -> Candidate:
        """
        Main entry point for parsing a resume file into a Candidate model.
        """
        filename = original_filename or os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower().replace(".", "") or "pdf"
        
        raw_text = cls.extract_raw_text(filepath)
        cleaned = clean_text(raw_text)
        
        if not cleaned:
            # Return empty or unparseable candidate structure safely
            return Candidate(
                filename=filename,
                filepath=filepath,
                file_type=ext,
                name="Unreadable / Empty Document",
                raw_text="",
                cleaned_text="",
                experience_text="Unable to determine",
                education_level="Not detected"
            )

        # Extract core fields
        email = cls.extract_email(cleaned)
        phone = cls.extract_phone(cleaned)
        name = cls.extract_name(cleaned, email=email)
        location = cls.extract_location(cleaned)
        
        # Extract skills, education, experience, certs
        skills = extract_skills_from_text(cleaned)
        certs = extract_certifications_from_text(cleaned)
        highest_degree, edu_records = extract_education_from_text(cleaned)
        total_years, exp_text, exp_records = parse_experience_years(cleaned)
        
        candidate = Candidate(
            filename=filename,
            filepath=filepath,
            file_type=ext,
            name=name,
            email=email,
            phone=phone,
            location=location,
            skills=skills,
            certifications=certs,
            education_level=highest_degree,
            education_records=edu_records,
            total_experience_years=total_years,
            experience_text=exp_text,
            experience_records=exp_records,
            raw_text=raw_text,
            cleaned_text=cleaned
        )
        
        return candidate
