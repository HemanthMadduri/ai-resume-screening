import re
from typing import List, Dict, Tuple, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models.candidate import JobDescription, Candidate
from services.text_processor import (
    clean_text,
    extract_skills_from_text,
    extract_education_from_text,
    DEGREE_LEVELS
)

class NLPAnalyzer:
    """NLP and semantic analysis service for Job Descriptions and Candidate Resumes."""

    @staticmethod
    def parse_job_description(jd_text: str, custom_title: str = "") -> JobDescription:
        """
        Analyze and extract structured requirements from a Job Description text.
        Separates required skills, preferred skills, min experience, and required education.
        """
        cleaned = clean_text(jd_text)
        
        # 1. Job Title detection
        title = custom_title
        if not title:
            title_match = re.search(r'(?:Job\s+Title|Role|Position):\s*([^\n]+)', cleaned, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                first_line = cleaned.split("\n")[0].strip()
                if len(first_line) < 60 and not re.search(r'requirements|responsibilities|overview', first_line, re.IGNORECASE):
                    title = first_line
                else:
                    title = "Target Job Role"

        # 2. Section segmentation: Required vs Preferred
        required_skills: List[str] = []
        preferred_skills: List[str] = []
        
        # Look for section headings
        req_pattern = r'(?:required|must\s+have|requirements|qualifications|core\s+skills|minimum\s+qualifications)([\s\S]*?)(?:preferred|nice\s+to\s+have|bonus|plus|good\s+to\s+have|about\s+the\s+company|benefits|responsibilities|$)'
        pref_pattern = r'(?:preferred|nice\s+to\s+have|bonus|plus|good\s+to\s+have|additional\s+qualifications)([\s\S]*?)(?:required|must\s+have|about\s+the\s+company|benefits|responsibilities|$)'
        
        req_match = re.search(req_pattern, cleaned, re.IGNORECASE)
        pref_match = re.search(pref_pattern, cleaned, re.IGNORECASE)
        
        all_skills = extract_skills_from_text(cleaned)
        
        if req_match:
            req_text = req_match.group(1)
            req_extracted = extract_skills_from_text(req_text)
            required_skills.extend(req_extracted)
            
        if pref_match:
            pref_text = pref_match.group(1)
            pref_extracted = extract_skills_from_text(pref_text)
            preferred_skills.extend([s for s in pref_extracted if s not in required_skills])
            
        # If no explicit sectioning detected, treat all extracted skills as required
        if not required_skills and not preferred_skills:
            required_skills = all_skills
        else:
            # Any remaining unclassified skills
            for s in all_skills:
                if s not in required_skills and s not in preferred_skills:
                    required_skills.append(s)

        # 3. Minimum Experience Years detection
        min_exp_years = 0.0
        jd_exp_patterns = [
            r'(?:min(?:imum)?\s+)?experience(?:\s+required)?\s*[:-]\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
            r'(\d+(?:\.\d+)?)\s*(?:\+|-|\s*to\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:relevant|professional|industry|hands-on|work|software|backend|frontend|fullstack|engineering|development|technical)?\s*(?:experience|exp)',
            r'(?:at\s+least|minimum|min)\s+(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
            r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+of\s+[\w\s]{0,25}(?:development|engineering|architecture|administration)',
            r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:working\s+with|in\s+software|in\s+tech)'
        ]
        found_exp_vals = []
        for pat in jd_exp_patterns:
            matches = re.findall(pat, cleaned, re.IGNORECASE)
            for m in matches:
                try:
                    val = float(m)
                    if 0.5 <= val <= 25:
                        found_exp_vals.append(val)
                except ValueError:
                    pass
        if found_exp_vals:
            min_exp_years = min(found_exp_vals)

        # 4. Required Education detection
        edu_header_match = re.search(r'Education(?:\s+Required)?:\s*([^\n]+)', cleaned, re.IGNORECASE)
        required_edu = "Bachelor's"
        if edu_header_match:
            header_edu_text = edu_header_match.group(1).strip()
            detected_from_header, _ = extract_education_from_text(header_edu_text)
            if detected_from_header != "Not detected":
                required_edu = detected_from_header
            elif re.search(r'\bmaster\b', header_edu_text, re.IGNORECASE):
                required_edu = "Master's"
            elif re.search(r'\bph\.?d|doctorate\b', header_edu_text, re.IGNORECASE):
                required_edu = "PhD"
            elif re.search(r'\bbachelor\b', header_edu_text, re.IGNORECASE):
                required_edu = "Bachelor's"
            elif re.search(r'\bdiploma|associate\b', header_edu_text, re.IGNORECASE):
                required_edu = "Diploma/Associate"
            elif re.search(r'\bany\b', header_edu_text, re.IGNORECASE):
                required_edu = "Any"
        else:
            highest_degree, _ = extract_education_from_text(cleaned)
            required_edu = highest_degree if highest_degree != "Not detected" else "Bachelor's"

        # 5. Extract top keywords using TF-IDF
        keywords = NLPAnalyzer.extract_top_keywords(cleaned, top_n=12)

        return JobDescription(
            title=title,
            raw_text=cleaned,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_experience_years=min_exp_years,
            required_education=required_edu,
            keywords=keywords
        )

    @staticmethod
    def extract_top_keywords(text: str, top_n: int = 15) -> List[str]:
        """Extract dominant meaningful keyword terms using TF-IDF."""
        if not text.strip():
            return []
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=top_n * 2,
                token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z0-9_-]+\b'
            )
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Sort by score descending
            sorted_indices = np.argsort(scores)[::-1]
            keywords = []
            for idx in sorted_indices:
                word = feature_names[idx]
                if len(word) > 2 and word not in keywords:
                    keywords.append(word.title())
                if len(keywords) >= top_n:
                    break
            return keywords
        except Exception:
            return []

    @staticmethod
    def calculate_tfidf_similarity(candidate_text: str, jd_text: str) -> float:
        """
        Compute normalized cosine similarity percentage (0.0 - 100.0)
        between candidate resume text and job description using TF-IDF.
        """
        if not candidate_text.strip() or not jd_text.strip():
            return 0.0
            
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                sublinear_tf=True,
                token_pattern=r'(?u)\b[a-zA-Z0-9_.+#-]+\b'
            )
            tfidf_matrix = vectorizer.fit_transform([candidate_text, jd_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Rescale slightly for human readability (pure cosine similarity on resumes tends to cluster in 0.15 - 0.70 range)
            scaled_sim = min(100.0, max(0.0, float(sim * 100 * 1.35)))
            return round(scaled_sim, 1)
        except Exception:
            return 0.0
