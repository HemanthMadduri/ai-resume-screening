import unittest
import os
import sys
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app


class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_dashboard_route(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TalentAI", response.data)

    def test_results_route(self):
        response = self.client.get("/results")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Candidate Rankings", response.data)

    def test_sample_jds_api(self):
        response = self.client.get("/api/sample-jds")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get("success"))
        self.assertTrue(len(data.get("samples", [])) > 0)

    def test_load_sample_and_export_api(self):
        # 1. Load sample data
        resp = self.client.post("/api/load-sample", json={"jd_type": "senior_fullstack_engineer"})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data.get("success"))
        self.assertTrue(len(data.get("candidates", [])) >= 5)

        # 2. Get candidates
        cands_resp = self.client.get("/api/candidates")
        self.assertEqual(cands_resp.status_code, 200)
        cands_data = json.loads(cands_resp.data)
        self.assertTrue(len(cands_data.get("candidates", [])) >= 5)

        # 3. Test Shortlist toggle
        cand_id = cands_data["candidates"][0]["id"]
        shortlist_resp = self.client.post(f"/api/candidate/{cand_id}/shortlist")
        self.assertEqual(shortlist_resp.status_code, 200)

        # 4. Test Notes update
        notes_resp = self.client.post(f"/api/candidate/{cand_id}/notes", json={"notes": "Excellent candidate for tech interview."})
        self.assertEqual(notes_resp.status_code, 200)

        # 5. Export CSV
        csv_resp = self.client.get("/api/export?format=csv")
        self.assertEqual(csv_resp.status_code, 200)
        self.assertIn(b"Overall Score", csv_resp.data)

        # 6. Export JSON
        json_resp = self.client.get("/api/export?format=json")
        self.assertEqual(json_resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
