import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ats-ai-screening-secret-key-2026")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")
    RESULTS_FOLDER = os.path.join(BASE_DIR, "data", "results")
    SAMPLES_FOLDER = os.path.join(BASE_DIR, "data", "samples")
    
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    
    # Configurable Scoring Weights (Must sum to 1.0)
    SCORING_WEIGHTS = {
        "skills": 0.40,          # 40% Skills Match
        "experience": 0.25,      # 25% Experience Match
        "education": 0.15,       # 15% Education Match
        "similarity": 0.10,      # 10% JD-Resume Semantic/TF-IDF Similarity
        "certifications": 0.10   # 10% Certifications & Additional Qualifications
    }

    # Recommendation Thresholds
    SCORE_THRESHOLDS = {
        "excellent": 85.0,
        "strong": 75.0,
        "consider": 60.0,
        "weak": 45.0
    }
