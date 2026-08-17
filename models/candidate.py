from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime

@dataclass
class ScoreBreakdown:
    skills_score: float = 0.0          # 0 - 100
    experience_score: float = 0.0      # 0 - 100
    education_score: float = 0.0       # 0 - 100
    similarity_score: float = 0.0      # 0 - 100
    certifications_score: float = 0.0  # 0 - 100
    overall_score: float = 0.0         # 0 - 100
    
    # Weighted contribution points
    skills_weighted: float = 0.0
    experience_weighted: float = 0.0
    education_weighted: float = 0.0
    similarity_weighted: float = 0.0
    certifications_weighted: float = 0.0

@dataclass
class JobDescription:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Software Professional"
    raw_text: str = ""
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    min_experience_years: float = 0.0
    required_education: str = "Bachelor's"
    keywords: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Candidate:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    filepath: str = ""
    file_type: str = "pdf"
    
    # Extracted Details
    name: str = "Not detected"
    email: str = "Not detected"
    phone: str = "Not detected"
    location: str = "Not detected"
    
    skills: List[str] = field(default_factory=list)
    total_experience_years: Optional[float] = None
    experience_text: str = "Unable to determine"
    experience_records: List[Dict[str, Any]] = field(default_factory=list)
    
    education_level: str = "Not detected"
    education_records: List[Dict[str, Any]] = field(default_factory=list)
    
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    
    raw_text: str = ""
    cleaned_text: str = ""
    
    # Analysis & Ranking
    rank: int = 0
    score_breakdown: ScoreBreakdown = field(default_factory=ScoreBreakdown)
    recommendation: str = "Under Review"
    
    matched_required_skills: List[str] = field(default_factory=list)
    matched_preferred_skills: List[str] = field(default_factory=list)
    missing_required_skills: List[str] = field(default_factory=list)
    missing_preferred_skills: List[str] = field(default_factory=list)
    
    # Explainability
    why_ranked_highly: List[str] = field(default_factory=list)
    potential_gaps: List[str] = field(default_factory=list)
    
    # Recruiter Workflow State
    status: str = "New"               # New, Screening, Shortlisted, Interview, Rejected, Hired
    is_shortlisted: bool = False
    notes: str = ""
    uploaded_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Candidate":
        if "score_breakdown" in data and isinstance(data["score_breakdown"], dict):
            data["score_breakdown"] = ScoreBreakdown(**data["score_breakdown"])
        return cls(**data)
