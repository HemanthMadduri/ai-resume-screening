import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.text_processor import (
    clean_text,
    extract_skills_from_text,
    extract_education_from_text,
    parse_experience_years,
    normalize_skill_name
)
from services.resume_parser import ResumeParser


class TestResumeParser(unittest.TestCase):

    def test_clean_text(self):
        dirty = "John   Doe\n\n\n\nSoftware   Engineer\t\twith ‘Python’ and “ML”."
        cleaned = clean_text(dirty)
        self.assertIn("John Doe", cleaned)
        self.assertIn("with 'Python' and \"ML\".", cleaned)

    def test_skill_aliases_and_extraction(self):
        text = "Experienced with Python, ML, NLP, k8s, React.js, PostgreSQL, and AWS."
        skills = extract_skills_from_text(text)
        self.assertIn("Python", skills)
        self.assertIn("Machine Learning", skills)
        self.assertIn("Natural Language Processing", skills)
        self.assertIn("Kubernetes", skills)
        self.assertIn("React", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertIn("AWS", skills)

    def test_email_and_phone_extraction(self):
        sample_text = "Contact: jane.developer@company.org | Phone: (555) 234-5678 | Address: New York"
        email = ResumeParser.extract_email(sample_text)
        phone = ResumeParser.extract_phone(sample_text)
        self.assertEqual(email, "jane.developer@company.org")
        self.assertIn("555", phone)

    def test_experience_parsing(self):
        exp_text_1 = "Senior Developer (2019 - 2023) at Acme Corp. Total 5+ years of experience."
        years, summary, records = parse_experience_years(exp_text_1)
        self.assertIsNotNone(years)
        self.assertGreaterEqual(years, 4.0)

    def test_education_parsing(self):
        edu_text = "Master of Science in Computer Science, Stanford University. Bachelor of Technology in IT."
        deg_level, records = extract_education_from_text(edu_text)
        self.assertEqual(deg_level, "Master's")

    def test_nonexistent_or_empty_file_graceful_handling(self):
        cand = ResumeParser.parse_resume("non_existent_file.pdf")
        self.assertEqual(cand.name, "Unreadable / Empty Document")
        self.assertEqual(cand.education_level, "Not detected")


if __name__ == "__main__":
    unittest.main()
