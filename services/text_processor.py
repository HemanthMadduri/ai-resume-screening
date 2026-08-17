import re
import string
from typing import List, Set, Dict, Tuple, Optional
from datetime import datetime

# Standard skill aliases mapping variant/acronym -> canonical name
SKILL_ALIASES: Dict[str, str] = {
    # AI / ML / Data
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "machine-learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "keras": "Keras",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "opencv": "OpenCV",
    "spacy": "spaCy",
    "nltk": "NLTK",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "data analytics": "Data Analysis",
    "data engineering": "Data Engineering",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",

    # Programming Languages
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c": "C",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "scala": "Scala",
    "r": "R",
    "sql": "SQL",
    "bash": "Bash/Shell",
    "shell": "Bash/Shell",
    "powershell": "PowerShell",

    # Web & Frameworks
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "angular": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "asp.net": "ASP.NET",
    "dotnet": ".NET",
    ".net": ".NET",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "graphql": "GraphQL",
    "rest": "REST API",
    "rest api": "REST API",
    "restful api": "REST API",
    "restful": "REST API",
    "websockets": "WebSockets",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "redux": "Redux",

    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",
    "dynamodb": "DynamoDB",
    "oracle": "Oracle DB",
    "firebase": "Firebase",
    "snowflake": "Snowflake",
    "bigquery": "BigQuery",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "linux": "Linux",
    "nginx": "Nginx",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "microservices": "Microservices",

    # Software Engineering & Methodologies
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "unit testing": "Unit Testing",
    "tdd": "TDD",
    "system design": "System Design",
    "oop": "OOP",
    "object oriented programming": "OOP",
    "design patterns": "Design Patterns",
    "problem solving": "Problem Solving"
}

# Certifications taxonomy
KNOWN_CERTIFICATIONS: List[str] = [
    "AWS Certified Solutions Architect",
    "AWS Certified Developer",
    "AWS Certified Cloud Practitioner",
    "CKA",
    "Certified Kubernetes Administrator",
    "Azure Fundamentals",
    "Azure Solutions Architect",
    "GCP Professional Cloud Architect",
    "PMP",
    "Project Management Professional",
    "CISSP",
    "CompTIA Security+",
    "TensorFlow Developer Certificate",
    "DeepLearning.AI Specialization",
    "Certified Scrum Master",
    "CSM",
    "Oracle Certified Professional"
]

# Degree levels hierarchy
DEGREE_LEVELS: Dict[str, int] = {
    "phd": 5,
    "doctorate": 5,
    "master": 4,
    "m.tech": 4,
    "mtech": 4,
    "m.s.": 4,
    "ms": 4,
    "msc": 4,
    "mba": 4,
    "bachelor": 3,
    "b.tech": 3,
    "btech": 3,
    "b.e.": 3,
    "be": 3,
    "b.s.": 3,
    "bs": 3,
    "bsc": 3,
    "bca": 3,
    "diploma": 2,
    "associate": 2,
    "high school": 1,
    "secondary": 1
}


def clean_text(text: str) -> str:
    """Normalize raw extracted text, strip irregular whitespace and unprintable characters."""
    if not text:
        return ""
    # Normalize unicode quotes and dashes
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    # Replace non-breaking spaces and tabs
    text = re.sub(r'[\t\r\f\v]', ' ', text)
    # Collapse multiple newlines/spaces
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def normalize_skill_name(skill: str) -> str:
    """Map a skill string to its canonical formatted name."""
    skill_clean = skill.strip().lower()
    return SKILL_ALIASES.get(skill_clean, skill.strip().title())


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract technical and professional skills from text using boundary-safe regex 
    matching against the comprehensive skill taxonomy and aliases.
    """
    if not text:
        return []
    
    text_lower = " " + text.lower() + " "
    # Replace punctuation (except +, #, /, .) with space for safer token extraction
    sanitized_text = re.sub(r'[,;:!?()\[\]{}|"\']', ' ', text_lower)
    
    found_skills: Set[str] = set()

    # Sort aliases by length descending to match multi-word phrases first (e.g. "machine learning" before "c")
    sorted_aliases = sorted(SKILL_ALIASES.keys(), key=len, reverse=True)
    
    for alias in sorted_aliases:
        canonical = SKILL_ALIASES[alias]
        # For very short single/two-letter terms like 'c', 'r', 'go', 'js', 'ts', require strict word boundaries
        if len(alias) <= 2 and alias in {"c", "r", "go", "js", "ts", "py", "ml", "dl", "cv", "ai", "tf"}:
            pattern = rf'(?<![a-zA-Z0-9_#+]){re.escape(alias)}(?![a-zA-Z0-9_#+])'
        elif alias in {"c++", "c#"}:
            pattern = rf'(?<![a-zA-Z0-9_]){re.escape(alias)}(?![a-zA-Z0-9_])'
        elif "." in alias or "/" in alias or "-" in alias:
            pattern = rf'(?<![a-zA-Z0-9_]){re.escape(alias)}(?![a-zA-Z0-9_])'
        else:
            pattern = rf'\b{re.escape(alias)}\b'
            
        if re.search(pattern, text_lower) or re.search(pattern, sanitized_text):
            found_skills.add(canonical)
            
    # Also search for known certifications
    for cert in KNOWN_CERTIFICATIONS:
        if cert.lower() in text_lower:
            found_skills.add(cert)
            
    return sorted(list(found_skills))


def extract_certifications_from_text(text: str) -> List[str]:
    """Detect professional certifications mentioned in resume text."""
    if not text:
        return []
    
    found_certs = []
    text_lower = text.lower()
    
    for cert in KNOWN_CERTIFICATIONS:
        if cert.lower() in text_lower:
            found_certs.append(cert)
            
    # Generic patterns like 'AWS Certified...', 'Certified Kubernetes...', 'Google Cloud Certified...'
    generic_patterns = [
        r'(?:AWS\s+Certified\s+[\w\s]+)',
        r'(?:Google\s+Cloud\s+Certified\s+[\w\s]+)',
        r'(?:Microsoft\s+Certified:\s+[\w\s]+)',
        r'(?:Certified\s+[\w\s]+\s+Professional)',
        r'(?:Oracle\s+Certified\s+[\w\s]+)'
    ]
    for pattern in generic_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            clean_m = m.strip()
            if len(clean_m) < 45 and clean_m not in found_certs:
                found_certs.append(clean_m)
                
    return list(dict.fromkeys(found_certs))


def extract_education_from_text(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Identify degree level (Bachelor's, Master's, PhD, Diploma) and education records.
    Returns (highest_degree_level, records_list).
    """
    if not text:
        return "Not detected", []
    
    records = []
    highest_score = 0
    highest_degree = "Not detected"
    
    # Common degree patterns
    degree_regexes = [
        (r'\b(ph\.?d|doctorate|doctor of philosophy)\b', "PhD", 5),
        (r'\b(m\.?tech|master of technology|m\.?s\.?|master of science|msc|mba|mca|master\'?s?(?:\s+degree)?)\b', "Master's", 4),
        (r'\b(b\.?tech|bachelor of technology|b\.?e\.?|bachelor of engineering|b\.?s\.?|bachelor of science|bsc|bca|bachelor\'?s?(?:\s+degree)?)\b', "Bachelor's", 3),
        (r'\b(diploma|associate(?:\s+degree)?)\b', "Diploma/Associate", 2),
        (r'\b(high school|higher secondary|12th|hsc)\b', "High School", 1)
    ]
    
    # Check degree levels
    for regex_pat, degree_name, score in degree_regexes:
        matches = re.finditer(regex_pat, text, re.IGNORECASE)
        for m in matches:
            if score > highest_score:
                highest_score = score
                highest_degree = degree_name
            # Grab context surrounding degree
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 70)
            snippet = clean_text(text[start:end]).replace("\n", " ")
            records.append({
                "degree": degree_name,
                "detail": snippet
            })
            
    # Deduplicate records
    unique_records = []
    seen_degrees = set()
    for r in records:
        if r["degree"] not in seen_degrees:
            unique_records.append(r)
            seen_degrees.add(r["degree"])
            
    return highest_degree, unique_records


def parse_experience_years(text: str) -> Tuple[Optional[float], str, List[Dict[str, str]]]:
    """
    Extract total estimated years of work experience and detected work history entries.
    Returns (total_years, experience_summary_text, work_records).
    """
    if not text:
        return None, "Unable to determine", []
    
    records = []
    current_year = datetime.now().year
    
    # Pattern 1: Explicit statements like "5+ years of experience", "3 years experience", "4.5 yrs experience"
    explicit_pattern = r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp|working|industry\s+experience)'
    explicit_matches = re.findall(explicit_pattern, text, re.IGNORECASE)
    
    explicit_years = []
    for match in explicit_matches:
        try:
            val = float(match)
            if 0.5 <= val <= 40:
                explicit_years.append(val)
        except ValueError:
            pass
            
    # Pattern 2: Date ranges like "2018 - 2023", "Jan 2019 - Present", "06/2020 – 11/2022"
    date_range_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(20\d{2}|19\d{2}|present|current|now)'
    
    date_matches = list(re.finditer(date_range_pattern, text, re.IGNORECASE))
    calculated_years = 0.0
    year_ranges = []
    
    for m in date_matches:
        start_year = int(m.group(2))
        end_str = m.group(4).lower()
        if end_str in ("present", "current", "now"):
            end_year = current_year
        else:
            try:
                end_year = int(end_str)
            except ValueError:
                end_year = current_year
                
        if 1990 <= start_year <= current_year and end_year >= start_year:
            duration = max(0.5, float(end_year - start_year))
            # Don't add absurd ranges (e.g. 1990 - 2026 for college/highschool)
            if duration <= 30:
                year_ranges.append((start_year, end_year, duration))
                # Grab snippet for record
                ctx_start = max(0, m.start() - 40)
                ctx_end = min(len(text), m.end() + 60)
                snippet = clean_text(text[ctx_start:ctx_end]).replace("\n", " ")
                records.append({
                    "duration": f"{start_year} - {m.group(4).title()}",
                    "years": duration,
                    "detail": snippet
                })

    # Estimate total years from non-overlapping ranges or sum of plausible jobs
    if year_ranges:
        # Merge overlapping year ranges
        year_ranges.sort(key=lambda x: x[0])
        merged = []
        for r in year_ranges:
            if not merged:
                merged.append([r[0], r[1]])
            else:
                prev = merged[-1]
                if r[0] <= prev[1]:
                    prev[1] = max(prev[1], r[1])
                else:
                    merged.append([r[0], r[1]])
        total_span = sum(m[1] - m[0] for m in merged)
        if total_span > 0:
            calculated_years = float(total_span)

    # Determine final years of experience
    final_years: Optional[float] = None
    if explicit_years:
        final_years = max(explicit_years)
    elif calculated_years > 0:
        final_years = calculated_years

    if final_years is not None:
        if final_years == int(final_years):
            exp_text = f"{int(final_years)} years"
        else:
            exp_text = f"{final_years:.1f} years"
    else:
        exp_text = "Unable to determine"

    return final_years, exp_text, records
