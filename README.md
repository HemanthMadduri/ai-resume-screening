# TalentAI ATS - AI Resume Screening & Candidate Ranking System

An intelligent, explainable, and production-grade **Applicant Tracking System (ATS)** built using **Vanilla HTML5, CSS3, JavaScript** on the frontend and **Python, Flask, spaCy, and scikit-learn** on the backend.

The system runs **100% locally** using local NLP and Machine Learning techniques. It requires **no paid external AI APIs** (No OpenAI, Gemini, or Claude API dependencies) while performing genuine semantic text analysis, skill extraction, qualification matching, and transparent candidate ranking.

---

## 🌟 Key Features

### 1. Multi-Format Resume Parsing
- Supports **PDF**, **DOCX**, and **TXT** files.
- Extracts candidate name (using **spaCy NER** and header heuristics), email, phone, location, work experience timeline, education qualifications, technical skills, and certifications.
- Resilient error handling: handles unreadable or corrupted files gracefully without crashing bulk operations.

### 2. Intelligent NLP & Skill Graph Matching
- Canonical skill taxonomy mapping aliases, acronyms, and synonyms (e.g., `ML` ↔ `Machine Learning`, `k8s` ↔ `Kubernetes`, `ReactJS` ↔ `React`, `Postgres` ↔ `PostgreSQL`).
- Boundary-safe n-gram phrase detection preventing false positives (e.g. `C` inside `CSS` or `R` inside `React`).
- TF-IDF vectorization with n-grams (1, 2) and sublinear scaling to compute lexical semantic cosine similarity between resumes and the Job Description.

### 3. Transparent Weighted Candidate Ranking
Configurable scoring formula balancing 5 key professional criteria:
$$\text{Overall Score} = (0.40 \times \text{Skills}) + (0.25 \times \text{Experience}) + (0.15 \times \text{Education}) + (0.10 \times \text{JD Similarity}) + (0.10 \times \text{Certifications})$$

- **Recommendation Categories**:
  - `85% - 100%`: **Excellent Match**
  - `75% - 84%`: **Strong Match**
  - `60% - 74%`: **Good Fit / Consider**
  - `45% - 59%`: **Moderate / Weak Match**
  - `< 45%`: **Low Match**

### 4. AI & NLP Explainability
- For every candidate, the system generates human-readable explanations explaining **why they ranked highly** (e.g., specific skills matched, experience duration) and **potential gaps / areas to verify** (missing required skills, educational alignment).

### 5. Ethical AI & Bias-Free Safeguards
- Strictly enforces qualification-based evaluation. **No protected demographic characteristics** (gender, age, race, religion, nationality, disability, photo, marital status) are ever used in scoring calculations.

### 6. Recruiter Workflow & Management
- Interactive candidate inspection modal with visual score breakdown meters, matched skill chips (green) vs. missing skill chips (red/amber), work history timeline, and education details.
- Shortlist candidates (★), update recruitment lifecycle statuses (`New`, `Screening`, `Shortlisted`, `Interview`, `Rejected`, `Hired`), and save persistent recruiter notes.
- Real-time client-side search (by name, email, skills, company) and multi-factor filters (minimum score slider, recommendation, status).
- 1-click export to **CSV** and **JSON**.

---

## 🛠️ Technology Stack

- **Frontend**:
  - **HTML5**: Semantic document structure.
  - **CSS3**: Vanilla CSS with custom properties (Dark / Light mode support), CSS Grid, Flexbox, glassmorphism accents, and responsive layout (Strictly zero Tailwind/Bootstrap/UI frameworks).
  - **JavaScript**: Pure Vanilla ES6+ for DOM manipulation, asynchronous uploads, toast notifications, and SVG charts (Strictly zero React/Vue/Angular/jQuery).
- **Backend**:
  - **Python 3.10+ / 3.13**
  - **Flask 3.x**: RESTful API and template rendering.
  - **spaCy (`en_core_web_sm`)**: Named Entity Recognition (NER), tokenization, and linguistic analysis.
  - **scikit-learn**: `TfidfVectorizer` and Cosine Similarity calculation.
  - **pdfplumber & PyPDF2**: Multi-tier PDF text extraction.
  - **python-docx**: Microsoft Word document extraction.
  - **ReportLab**: Programmatic document generation for demo data.

---

## 📁 Project Structure

```text
ai-resume-screening/
│
├── app.py                     # Flask application entry point & API endpoints
├── config.py                  # System configuration (weights, thresholds, upload limits)
├── generate_samples.py        # Demo dataset generator (sample resumes & JDs)
├── requirements.txt           # Python dependencies
├── README.md                  # System documentation
│
├── data/
│   ├── uploads/               # Uploaded resume repository
│   ├── results/               # Session cache & saved state (JSON)
│   └── samples/               # Realistic sample resumes (.pdf, .docx, .txt) & JDs
│       ├── sample_jds/
│       │   ├── senior_fullstack_engineer.txt
│       │   └── machine_learning_engineer.txt
│       └── sample_resumes/
│           ├── rahul_sharma_senior_ml.pdf
│           ├── priya_kumar_fullstack.docx
│           ├── arjun_patel_backend.txt
│           ├── sneha_rao_junior_dev.pdf
│           └── vikram_singh_devops.docx
│
├── models/
│   ├── __init__.py
│   └── candidate.py           # Data structures (Candidate, JobDescription, ScoreBreakdown)
│
├── services/
│   ├── __init__.py
│   ├── text_processor.py      # Cleaning, skill taxonomy, aliases, and experience/education parsing
│   ├── resume_parser.py       # Multi-format document parser (PDF, DOCX, TXT)
│   ├── nlp_analyzer.py        # JD parser, TF-IDF cosine similarity, and keyword extraction
│   └── ranking_engine.py      # Weighted ranking algorithm, explainability generator
│
├── templates/
│   ├── base.html              # Base layout with sidebar, navbar, modals, and toasts
│   ├── dashboard.html         # Recruiter dashboard (JD input, dropzone, queue, stats)
│   └── results.html           # Candidate rankings table, search, filters, and actions
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern ATS design system (Dark & Light themes)
│   └── js/
│       ├── app.js             # Main frontend controller (Async uploads, filters, notes, modals)
│       └── charts.js          # SVG circular gauges and score distribution meters
│
└── tests/
    ├── __init__.py
    ├── test_parser.py         # Unit tests for text cleaning and resume parsing
    ├── test_ranking.py        # Unit tests for scoring engine, weights, and bias prevention
    └── test_api.py            # Unit tests for Flask REST API routes
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Git (optional).

### 2. Clone / Open the Project
```bash
cd "C:\mini project\ai-resume-screening"
```

### 3. Create & Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Install the spaCy NLP Model
```bash
python -m spacy download en_core_web_sm
```

### 6. Generate Sample Resumes & JDs (Optional if already present)
```bash
python generate_samples.py
```

---

## 💻 Running the Application

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 Running Unit Tests

Run the automated test suite covering parsers, ranking algorithms, and API endpoints:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📋 Step-by-Step User Workflow

1. **Open Dashboard**:
   Navigate to `http://127.0.0.1:5000`. You will see KPI metric cards and dual workflow panels.
2. **Configure Job Description**:
   - Paste custom JD text, upload a `.txt` JD file, or select a built-in sample JD from the dropdown (e.g. *Senior Full Stack Engineer* or *Machine Learning & NLP Specialist*).
   - The detected requirements preview immediately updates with required skills, min experience, and required education.
3. **Upload Resumes**:
   - Drag & drop candidate resumes into the upload area or click **Browse Files**.
   - Supports batch uploads of 10–100+ files (.pdf, .docx, .txt).
   - Alternatively, click **"Load Demo Data"** in the top bar to instantly test with 5 pre-configured realistic candidate resumes.
4. **Screen & Rank Candidates**:
   - Click **"Analyze & Rank Candidates"**.
   - The NLP engine parses documents, cleans text, computes TF-IDF similarity, checks experience duration, evaluates education, and calculates transparent weighted scores.
5. **Explore Rankings & Filter**:
   - View ranked candidates sorted from highest to lowest match.
   - Filter by minimum score slider, search by name or skill, filter by recommendation or status, or view shortlisted only.
6. **Inspect Candidate Profile & Explainability**:
   - Click **"Inspect"** on any candidate to open their detailed modal.
   - View score breakdown meters, AI explainability points (strengths vs. gaps), matched vs. missing skills matrix, work history timeline, and education records.
7. **Recruiter Actions & Export**:
   - Toggle Shortlist (★), update status (e.g. `Interview`), and type recruiter notes.
   - Click **"Export CSV"** or **"Export JSON"** to download the screening report.

---

## ⚖️ Scoring Formula & Explainability

```text
Overall Score = (Skills_Match * 0.40) + (Experience_Match * 0.25) + (Education_Match * 0.15) + (JD_Similarity * 0.10) + (Certifications * 0.10)
```

| Factor | Weight | Evaluation Method |
| :--- | :---: | :--- |
| **Technical Skills Match** | **40%** | Ratio of required skills present in candidate resume (85% subweight) + bonus for preferred skills (15% subweight). |
| **Experience Match** | **25%** | Detected candidate years vs. JD minimum required experience years. |
| **Education Match** | **15%** | Candidate degree level (Bachelor's, Master's, PhD, Diploma) aligned against JD minimum requirement. |
| **Semantic JD Similarity** | **10%** | TF-IDF vectorizer with n-grams (1, 2) and sublinear scaling measuring Cosine Similarity between resume text and JD. |
| **Certifications & Verified Qualifications** | **10%** | Presence of verified industry certifications (e.g., AWS, CKA, PMP, Azure, DeepLearning.AI). |

---

## 🔒 Security & Privacy

- **Local Processing**: All resume parsing and NLP scoring occurs strictly on your local machine. No candidate data or resume contents are transmitted to external cloud APIs.
- **Path Traversal Protection**: Uploaded files are sanitized with `secure_filename` and isolated within `data/uploads/`.
- **Allowed Formats Only**: Strict MIME and extension validation limited to `.pdf`, `.docx`, and `.txt`.
- **Upload Size Limit**: 16 MB maximum per batch request.

---

## 📄 License
MIT License. Created for professional recruitment workflows and candidate ranking.
