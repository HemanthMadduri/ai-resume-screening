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

# Degree levels hierarchy (higher number = higher educational attainment)
DEGREE_LEVELS: Dict[str, int] = {
    # PhD / Doctorate (5)
    "phd": 5,
    "ph.d": 5,
    "doctorate": 5,
    "doctor of philosophy": 5,

    # Master's (4)
    "master's": 4,
    "masters": 4,
    "master": 4,
    "m.tech": 4,
    "mtech": 4,
    "m.s.": 4,
    "m.s": 4,
    "ms": 4,
    "msc": 4,
    "mba": 4,
    "mca": 4,
    "m.e.": 4,
    "me": 4,
    "master of science": 4,
    "master of technology": 4,
    "master of engineering": 4,
    "master of computer applications": 4,
    "master of business administration": 4,

    # Bachelor's (3)
    "bachelor's": 3,
    "bachelors": 3,
    "bachelor": 3,
    "b.tech": 3,
    "btech": 3,
    "b.e.": 3,
    "be": 3,
    "b.s.": 3,
    "b.s": 3,
    "bs": 3,
    "bsc": 3,
    "bca": 3,
    "bba": 3,
    "b.com": 3,
    "bcom": 3,
    "b.a.": 3,
    "ba": 3,
    "bachelor of science": 3,
    "bachelor of technology": 3,
    "bachelor of engineering": 3,
    "bachelor of computer applications": 3,
    "bachelor of arts": 3,

    # Associate / Diploma (2)
    "associate": 2,
    "associate's": 2,
    "associates": 2,
    "diploma": 2,
    "diploma/associate": 2,
    "associate degree": 2,
    "associate of science": 2,
    "associate of arts": 2,
    "a.s.": 2,
    "a.a.": 2,

    # High School (1)
    "high school": 1,
    "secondary": 1,
    "higher secondary": 1,
    "12th": 1,
    "hsc": 1,
}


def get_degree_level(degree_name: str) -> int:
    """Return numeric degree rank (0-5) for any degree variant."""
    if not degree_name:
        return 0
    clean = degree_name.strip().lower()
    if clean in DEGREE_LEVELS:
        return DEGREE_LEVELS[clean]
    no_apostrophe = clean.replace("'", "").replace("’", "")
    if no_apostrophe in DEGREE_LEVELS:
        return DEGREE_LEVELS[no_apostrophe]
    if any(k in clean for k in ["phd", "ph.d", "doctorate"]):
        return 5
    if any(k in clean for k in ["master", "m.tech", "mtech", "m.s.", "msc", "mba", "mca"]):
        return 4
    if any(k in clean for k in ["bachelor", "b.tech", "btech", "b.e.", "b.s.", "bsc", "bca"]):
        return 3
    if any(k in clean for k in ["associate", "diploma"]):
        return 2
    if any(k in clean for k in ["high school", "secondary"]):
        return 1
    return 0


def clean_text(text: str) -> str:
    """Normalize raw extracted text, strip irregular whitespace and unprintable characters."""
    if not text:
        return ""
    # Normalize unicode quotes and dashes
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    # Normalize common PDF ligatures
    text = text.replace("\ufb01", "fi").replace("\ufb02", "fl").replace("\ufb00", "ff").replace("\ufb03", "ffi").replace("\ufb04", "ffl")
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
    sanitized_text = re.sub(r'[,;:!?()\[\]{}|"\']', ' ', text_lower)
    
    found_skills: Set[str] = set()
    sorted_aliases = sorted(SKILL_ALIASES.keys(), key=len, reverse=True)
    
    for alias in sorted_aliases:
        canonical = SKILL_ALIASES[alias]
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
            
    generic_patterns = [
        r'(?:AWS\s+Certified\s+[\w\s]+)',
        r'(?:Google\s+Cloud\s+Certified\s+[\w\s]+)',
        r'(?:Microsoft\s+Certified:\s+[\w\s]+)',
        r'(?:Certified\s+[\w\s]+\s+Professional)',
        r'(?:Oracle\s+Certified\s+[\w\s]+)',
        r'(?:Meta\s+[\w\s\-]+Certificate)'
    ]
    for pattern in generic_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            clean_m = m.strip()
            if len(clean_m) < 45 and clean_m not in found_certs:
                found_certs.append(clean_m)
                
    return list(dict.fromkeys(found_certs))


def split_resume_into_sections(text: str) -> Dict[str, str]:
    """
    Split resume into logical sections: summary, experience, education, skills, certs, other.
    Ensures work experience dates and education dates are strictly separated.
    """
    sections: Dict[str, List[str]] = {
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "other": []
    }

    section_triggers = [
        (re.compile(r'^(?:professional\s+)?summary|profile|about\s+me|objective', re.IGNORECASE), "summary"),
        (re.compile(r'^(?:work\s+|professional\s+)?experience|employment\s+history|career\s+history|work\s+history', re.IGNORECASE), "experience"),
        (re.compile(r'^education|academic\s+background|academics|qualifications', re.IGNORECASE), "education"),
        (re.compile(r'^(?:technical\s+|core\s+)?skills|technologies|competencies', re.IGNORECASE), "skills"),
        (re.compile(r'^certifications|certificates|licenses', re.IGNORECASE), "certifications")
    ]

    current_section = "summary"
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        clean_heading = re.sub(r'[=_\-*#:]', '', stripped).strip()
        is_heading = False

        if 3 <= len(clean_heading) <= 35:
            for pattern, sec_name in section_triggers:
                if pattern.search(clean_heading):
                    current_section = sec_name
                    is_heading = True
                    break

        if not is_heading:
            sections[current_section].append(stripped)

    return {k: "\n".join(v) for k, v in sections.items()}


def extract_education_from_text(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Identify degree level (Bachelor's, Master's, PhD, Diploma/Associate) and education records.
    Returns (highest_degree_level, records_list).
    """
    if not text:
        return "Not detected", []
    
    sections = split_resume_into_sections(text)
    edu_text = sections.get("education", "")
    target_texts = [edu_text, text] if edu_text else [text]

    records = []
    highest_score = 0
    highest_degree = "Not detected"

    # Context-safe degree patterns
    degree_regexes = [
        (r'\b(ph\.?d|doctorate|doctor\s+of\s+philosophy)\b', "PhD", 5),
        # Avoid matching 'Scrum Master' or 'Webmaster'
        (r'(?<!scrum\s)(?<!certified\s)(?<!agile\s)\b(m\.?tech|master\s+of\s+technology|m\.?s\.?(?!\s+office|\s+excel|\s+word|\s+access|\s+sql)|master\s+of\s+science|msc|mba|mca|master\s+of\s+engineering|m\.?e\.?|master\'?s\s+degree)\b', "Master's", 4),
        (r'\b(b\.?tech|bachelor\s+of\s+technology|b\.?e\.?|bachelor\s+of\s+engineering|b\.?s\.?|bachelor\s+of\s+science|bsc|bca|bba|b\.?com|bachelor\'?s\s+degree|bachelor\s+degree|bachelor\s+of\s+arts|b\.?a\.)\b', "Bachelor's", 3),
        # Avoid matching job title 'Associate'
        (r'\b(associate(?:\'?s)?\s+degree|associate\s+of\s+(?:science|arts|applied\s+science)|a\.s\.\s+degree|a\.a\.\s+degree|diploma\s+in\s+[\w\s]+|polytechnic\s+diploma)\b', "Diploma/Associate", 2),
        (r'\b(high\s+school|higher\s+secondary|12th|hsc)\b', "High School", 1)
    ]

    for search_text in target_texts:
        if not search_text.strip():
            continue
        for regex_pat, degree_name, score in degree_regexes:
            matches = list(re.finditer(regex_pat, search_text, re.IGNORECASE))
            for m in matches:
                if score > highest_score:
                    highest_score = score
                    highest_degree = degree_name

                start = max(0, m.start() - 30)
                end = min(len(search_text), m.end() + 70)
                snippet = clean_text(search_text[start:end]).replace("\n", " ")
                records.append({
                    "degree": degree_name,
                    "detail": snippet
                })
        if highest_score > 0:
            break

    # Fallback search if still not detected
    if highest_degree == "Not detected":
        if re.search(r'\bbachelor\b', text, re.IGNORECASE):
            highest_degree = "Bachelor's"
        elif re.search(r'\bmaster\b', text, re.IGNORECASE) and not re.search(r'scrum\s+master', text, re.IGNORECASE):
            highest_degree = "Master's"

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
    Excludes education dates from inflating professional tenure.
    Returns (total_years, experience_summary_text, work_records).
    """
    if not text:
        return None, "Unable to determine", []

    records = []
    current_year = datetime.now().year
    current_month = datetime.now().month

    sections = split_resume_into_sections(text)
    exp_section = sections.get("experience", "")
    summary_section = sections.get("summary", "")

    # Comprehensive explicit patterns (e.g. "3.5 years of experience", "Total Experience: 4+ yrs")
    explicit_patterns = [
        r'(?:total\s+)?(?:work\s+|professional\s+|relevant\s+)?experience(?:\s+required)?\s*[:-]\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
        r'(\d+(?:\.\d+)?)\s*(?:\+|-|\s*to\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:relevant|professional|industry|hands-on|work|software|backend|frontend|fullstack|engineering|development|technical)?\s*(?:experience|exp)',
        r'(?:over|minimum|at\s+least|approx(?:imately)?)\s+(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:[\w\s]{0,20})?(?:experience|exp)',
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+in\s+(?:software|web|backend|frontend|fullstack|data|machine|cloud|devops|engineering|development)',
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:building|developing|designing|managing|architecting)'
    ]

    explicit_years = []
    # Check summary section first for high-confidence self-stated total
    for pat in explicit_patterns:
        matches = re.findall(pat, summary_section or text, re.IGNORECASE)
        for m in matches:
            try:
                val = float(m)
                if 0.5 <= val <= 40:
                    explicit_years.append(val)
            except ValueError:
                pass

    month_lookup = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9, 'sept': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }

    # Restrict date ranges strictly to Work Experience section if present,
    # or full text excluding education section
    scan_text = exp_section if exp_section.strip() else text
    if not exp_section.strip() and sections.get("education"):
        # Strip out education text to avoid college graduation years counting as work experience
        scan_text = scan_text.replace(sections["education"], "")

    date_range_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?(20\d{2}|19\d{2}|present|current|now)'
    date_matches = list(re.finditer(date_range_pattern, scan_text, re.IGNORECASE))

    year_ranges = []

    for m in date_matches:
        start_month_str = (m.group(1) or "").strip().lower()
        start_month = 1
        for k, v in month_lookup.items():
            if start_month_str.startswith(k):
                start_month = v
                break

        start_year = int(m.group(2))
        end_month_str = (m.group(3) or "").strip().lower()
        end_month = 12
        for k, v in month_lookup.items():
            if end_month_str.startswith(k):
                end_month = v
                break

        end_str = m.group(4).lower()
        if end_str in ("present", "current", "now"):
            end_year = current_year
            end_month = current_month
        else:
            try:
                end_year = int(end_str)
            except ValueError:
                end_year = current_year
                end_month = current_month

        if 1990 <= start_year <= current_year and (end_year > start_year or (end_year == start_year and end_month >= start_month)):
            start_val = start_year + ((start_month - 1) / 12.0)
            end_val = end_year + (end_month / 12.0)
            duration = max(0.2, round(end_val - start_val, 1))

            if duration <= 35:
                year_ranges.append((start_val, end_val, duration, start_year, end_str))
                ctx_start = max(0, m.start() - 40)
                ctx_end = min(len(scan_text), m.end() + 60)
                snippet = clean_text(scan_text[ctx_start:ctx_end]).replace("\n", " ")
                records.append({
                    "duration": f"{start_year} - {m.group(4).title()}",
                    "years": duration,
                    "detail": snippet
                })

    calculated_years = 0.0
    if year_ranges:
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
            calculated_years = round(total_span, 1)

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

