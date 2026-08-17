import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.candidate import Candidate, JobDescription
from services.ranking_engine import RankingEngine
from services.nlp_analyzer import NLPAnalyzer


class TestRankingEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RankingEngine()
        self.sample_jd = JobDescription(
            title="Senior Python Backend Developer",
            raw_text="Looking for a Python developer with Django, PostgreSQL, Docker, and AWS. 3+ years experience. Bachelor's degree.",
            required_skills=["Python", "Django", "PostgreSQL", "Docker"],
            preferred_skills=["AWS", "Kubernetes"],
            min_experience_years=3.0,
            required_education="Bachelor's"
        )

    def test_strong_candidate_ranking(self):
        strong_cand = Candidate(
            name="Alice Smith",
            skills=["Python", "Django", "PostgreSQL", "Docker", "AWS"],
            total_experience_years=4.5,
            experience_text="4.5 years",
            education_level="Bachelor's",
            certifications=["AWS Certified Developer"],
            raw_text="Alice Smith. Senior Python Developer with 4.5 years exp in Django, PostgreSQL, Docker, AWS.",
            cleaned_text="alice smith senior python developer with 4.5 years exp in django postgresql docker aws"
        )

        junior_cand = Candidate(
            name="Bob Jones",
            skills=["Python", "HTML5"],
            total_experience_years=1.0,
            experience_text="1 year",
            education_level="Bachelor's",
            certifications=[],
            raw_text="Bob Jones. Junior developer with 1 year Python and HTML5.",
            cleaned_text="bob jones junior developer with 1 year python and html5"
        )

        ranked = self.engine.rank_candidates([strong_cand, junior_cand], self.sample_jd)

        # Alice should be Rank #1
        self.assertEqual(ranked[0].name, "Alice Smith")
        self.assertEqual(ranked[0].rank, 1)
        self.assertGreater(ranked[0].score_breakdown.overall_score, ranked[1].score_breakdown.overall_score)
        self.assertIn("Python", ranked[0].matched_required_skills)
        self.assertIn("Docker", ranked[0].matched_required_skills)
        self.assertGreaterEqual(ranked[0].score_breakdown.skills_score, 90.0)

    def test_explainability_generation(self):
        cand = Candidate(
            name="Test User",
            skills=["Python"],
            total_experience_years=1.0,
            experience_text="1 year",
            education_level="High School",
            raw_text="Python",
            cleaned_text="python"
        )
        self.engine.rank_candidates([cand], self.sample_jd)
        self.assertTrue(len(cand.potential_gaps) > 0)
        self.assertTrue(any("Missing" in g for g in cand.potential_gaps))

    def test_bias_free_scoring(self):
        # Two identical candidates except for demographic info in raw text
        cand1 = Candidate(
            name="Candidate One",
            skills=["Python", "Django", "PostgreSQL", "Docker"],
            total_experience_years=3.0,
            experience_text="3.0 years",
            education_level="Bachelor's",
            raw_text="Male, 28 years old, Nationality: US. Python Django PostgreSQL Docker.",
            cleaned_text="male 28 years old nationality us python django postgresql docker"
        )
        cand2 = Candidate(
            name="Candidate Two",
            skills=["Python", "Django", "PostgreSQL", "Docker"],
            total_experience_years=3.0,
            experience_text="3.0 years",
            education_level="Bachelor's",
            raw_text="Female, 45 years old, Nationality: IN. Python Django PostgreSQL Docker.",
            cleaned_text="female 45 years old nationality in python django postgresql docker"
        )
        self.engine.rank_candidates([cand1], self.sample_jd)
        self.engine.rank_candidates([cand2], self.sample_jd)

        # Qualification scores should be strictly equal
        self.assertAlmostEqual(cand1.score_breakdown.skills_score, cand2.score_breakdown.skills_score, places=1)
        self.assertAlmostEqual(cand1.score_breakdown.experience_score, cand2.score_breakdown.experience_score, places=1)
        self.assertAlmostEqual(cand1.score_breakdown.education_score, cand2.score_breakdown.education_score, places=1)


if __name__ == "__main__":
    unittest.main()
