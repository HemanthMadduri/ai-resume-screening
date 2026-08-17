from typing import List, Dict, Any, Optional, Tuple
import copy
from models.candidate import Candidate, JobDescription, ScoreBreakdown
from services.nlp_analyzer import NLPAnalyzer
from services.text_processor import DEGREE_LEVELS
from config import Config

class RankingEngine:
    """Calculates explainable, multi-factor, weighted match scores and ranks candidates."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or Config.SCORING_WEIGHTS
        # Ensure weights normalize to 1.0
        total_w = sum(self.weights.values())
        if total_w > 0:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

    def evaluate_skills_match(self, candidate: Candidate, jd: JobDescription) -> Tuple[float, List[str], List[str], List[str], List[str]]:
        """
        Evaluate candidate skills against JD required & preferred skills.
        Returns (skills_score_0_100, matched_req, missing_req, matched_pref, missing_pref).
        """
        cand_skills_set = {s.lower() for s in candidate.skills}
        
        # Required skills comparison
        matched_req = []
        missing_req = []
        for req in jd.required_skills:
            if req.lower() in cand_skills_set:
                matched_req.append(req)
            else:
                missing_req.append(req)
                
        # Preferred skills comparison
        matched_pref = []
        missing_pref = []
        for pref in jd.preferred_skills:
            if pref.lower() in cand_skills_set:
                matched_pref.append(pref)
            else:
                missing_pref.append(pref)

        # Scoring calculation
        req_score = 100.0
        if jd.required_skills:
            req_score = (len(matched_req) / len(jd.required_skills)) * 100.0

        pref_score = 100.0
        if jd.preferred_skills:
            pref_score = (len(matched_pref) / len(jd.preferred_skills)) * 100.0

        # Weighted combination: 85% required, 15% preferred
        if jd.preferred_skills:
            total_skill_score = (req_score * 0.85) + (pref_score * 0.15)
        else:
            total_skill_score = req_score

        return min(100.0, max(0.0, total_skill_score)), matched_req, missing_req, matched_pref, missing_pref

    def evaluate_experience_match(self, candidate: Candidate, jd: JobDescription) -> float:
        """
        Score candidate experience against JD required minimum years.
        """
        req_years = jd.min_experience_years
        cand_years = candidate.total_experience_years

        if req_years <= 0:
            # If JD doesn't require specific experience, award high score if candidate has any history
            if cand_years is not None and cand_years > 0:
                return 100.0
            return 80.0

        if cand_years is None:
            # Unknown experience
            return 35.0

        if cand_years >= req_years:
            # Meets or exceeds requirement
            # Slight bonus for seniority capped at 100
            return 100.0
        else:
            # Proportional score
            ratio = cand_years / req_years
            return round(max(15.0, ratio * 90.0), 1)

    def evaluate_education_match(self, candidate: Candidate, jd: JobDescription) -> float:
        """
        Score candidate education degree level against JD requirement.
        """
        req_level_num = DEGREE_LEVELS.get(jd.required_education.lower(), 3)
        cand_level_num = DEGREE_LEVELS.get(candidate.education_level.lower(), 0)

        if cand_level_num >= req_level_num and cand_level_num > 0:
            return 100.0
        elif cand_level_num == req_level_num - 1 and cand_level_num > 0:
            return 80.0
        elif cand_level_num > 0:
            return 60.0
        else:
            # Degree not detected
            return 45.0

    def evaluate_certifications_match(self, candidate: Candidate) -> float:
        """
        Score candidate certifications and additional verified qualifications.
        """
        num_certs = len(candidate.certifications)
        if num_certs >= 3:
            return 100.0
        elif num_certs == 2:
            return 85.0
        elif num_certs == 1:
            return 70.0
        elif len(candidate.skills) >= 8:
            # Diverse verified skills bonus even with no explicit certification
            return 50.0
        return 30.0

    def generate_explainability(self, candidate: Candidate, jd: JobDescription, breakdown: ScoreBreakdown) -> Tuple[List[str], List[str]]:
        """
        Generate human-readable AI explanation bullet points for why the candidate ranked 
        at their level, highlighting factual strengths and gaps.
        """
        why_ranked: List[str] = []
        potential_gaps: List[str] = []

        # 1. Skills explainability
        if jd.required_skills:
            if len(candidate.matched_required_skills) == len(jd.required_skills):
                why_ranked.append(f"Matches all {len(jd.required_skills)} required technical skills ({', '.join(candidate.matched_required_skills[:4])}).")
            elif len(candidate.matched_required_skills) > 0:
                why_ranked.append(f"Matches {len(candidate.matched_required_skills)} of {len(jd.required_skills)} required skills ({', '.join(candidate.matched_required_skills[:3])}).")
            
            if candidate.missing_required_skills:
                potential_gaps.append(f"Missing {len(candidate.missing_required_skills)} required skills: {', '.join(candidate.missing_required_skills[:4])}.")

        if candidate.matched_preferred_skills:
            why_ranked.append(f"Possesses {len(candidate.matched_preferred_skills)} preferred / bonus skills: {', '.join(candidate.matched_preferred_skills[:3])}.")

        # 2. Experience explainability
        cand_years = candidate.total_experience_years
        req_years = jd.min_experience_years
        if req_years > 0:
            if cand_years is not None:
                if cand_years >= req_years:
                    why_ranked.append(f"Has {cand_years:.1f} years of relevant experience, satisfying the {req_years:.1f}+ years requirement.")
                else:
                    potential_gaps.append(f"Detected {cand_years:.1f} years of experience vs {req_years:.1f} years requested in the Job Description.")
            else:
                potential_gaps.append("Total years of experience could not be definitively extracted from the resume format.")
        elif cand_years is not None and cand_years > 0:
            why_ranked.append(f"Brings {cand_years:.1f} years of demonstrated industry experience.")

        # 3. Education explainability
        if candidate.education_level != "Not detected":
            why_ranked.append(f"Holds a detected {candidate.education_level} qualification.")
        else:
            potential_gaps.append("Formal degree qualification was not explicitly detected in standard formats.")

        # 4. JD Similarity explainability
        if breakdown.similarity_score >= 70.0:
            why_ranked.append(f"Strong semantic alignment with Job Description context ({breakdown.similarity_score:.0f}% similarity index).")
        elif breakdown.similarity_score <= 35.0:
            potential_gaps.append(f"Lower contextual overlap with job description responsibilities ({breakdown.similarity_score:.0f}% similarity).")

        # 5. Certifications
        if candidate.certifications:
            why_ranked.append(f"Certified in {', '.join(candidate.certifications[:2])}.")

        return why_ranked, potential_gaps

    def assign_recommendation(self, score: float) -> str:
        """Assign category recommendation based on overall score."""
        if score >= Config.SCORE_THRESHOLDS["excellent"]:
            return "Excellent Match"
        elif score >= Config.SCORE_THRESHOLDS["strong"]:
            return "Strong Match"
        elif score >= Config.SCORE_THRESHOLDS["consider"]:
            return "Good Fit / Consider"
        elif score >= Config.SCORE_THRESHOLDS["weak"]:
            return "Moderate / Weak Match"
        else:
            return "Low Match"

    def rank_candidates(self, candidates: List[Candidate], jd: JobDescription) -> List[Candidate]:
        """
        Compute full weighted score for every candidate, sort descending,
        and generate rank positions and explainability.
        """
        for cand in candidates:
            # 1. Skills match
            s_score, m_req, mis_req, m_pref, mis_pref = self.evaluate_skills_match(cand, jd)
            cand.matched_required_skills = m_req
            cand.missing_required_skills = mis_req
            cand.matched_preferred_skills = m_pref
            cand.missing_preferred_skills = mis_pref

            # 2. Experience match
            exp_score = self.evaluate_experience_match(cand, jd)

            # 3. Education match
            edu_score = self.evaluate_education_match(cand, jd)

            # 4. JD Semantic Similarity (TF-IDF)
            sim_score = NLPAnalyzer.calculate_tfidf_similarity(cand.cleaned_text, jd.raw_text)

            # 5. Certifications match
            cert_score = self.evaluate_certifications_match(cand)

            # 6. Weighted overall score
            w_skills = self.weights.get("skills", 0.40)
            w_exp = self.weights.get("experience", 0.25)
            w_edu = self.weights.get("education", 0.15)
            w_sim = self.weights.get("similarity", 0.10)
            w_cert = self.weights.get("certifications", 0.10)

            skills_contrib = round(s_score * w_skills, 1)
            exp_contrib = round(exp_score * w_exp, 1)
            edu_contrib = round(edu_score * w_edu, 1)
            sim_contrib = round(sim_score * w_sim, 1)
            cert_contrib = round(cert_score * w_cert, 1)

            overall = round(skills_contrib + exp_contrib + edu_contrib + sim_contrib + cert_contrib, 1)
            overall = min(100.0, max(0.0, overall))

            breakdown = ScoreBreakdown(
                skills_score=round(s_score, 1),
                experience_score=round(exp_score, 1),
                education_score=round(edu_score, 1),
                similarity_score=round(sim_score, 1),
                certifications_score=round(cert_score, 1),
                overall_score=overall,
                skills_weighted=skills_contrib,
                experience_weighted=exp_contrib,
                education_weighted=edu_contrib,
                similarity_weighted=sim_contrib,
                certifications_weighted=cert_contrib
            )

            cand.score_breakdown = breakdown
            cand.recommendation = self.assign_recommendation(overall)

            # Generate explainability
            why_ranked, gaps = self.generate_explainability(cand, jd, breakdown)
            cand.why_ranked_highly = why_ranked
            cand.potential_gaps = gaps

        # Sort candidates descending by overall score
        candidates.sort(key=lambda c: (c.score_breakdown.overall_score, c.score_breakdown.skills_score), reverse=True)

        # Assign rank 1..N
        for idx, cand in enumerate(candidates, start=1):
            cand.rank = idx

        return candidates
