import os
import io
import csv
import json
import uuid
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_file,
    redirect,
    url_for
)
from werkzeug.utils import secure_filename

from config import Config
from models.candidate import Candidate, JobDescription, ScoreBreakdown
from services.resume_parser import ResumeParser
from services.nlp_analyzer import NLPAnalyzer
from services.ranking_engine import RankingEngine

app = Flask(__name__)
app.config.from_object(Config)

# Ensure data directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESULTS_FOLDER"], exist_ok=True)
os.makedirs(app.config["SAMPLES_FOLDER"], exist_ok=True)

# In-memory application state with persistence to JSON
CURRENT_STATE: Dict[str, Any] = {
    "job_description": None,
    "candidates": [],
    "last_analyzed_at": None
}

RESULTS_FILE = os.path.join(app.config["RESULTS_FOLDER"], "current_session.json")


def save_session_state():
    """Persist current session state to JSON file."""
    try:
        data = {
            "job_description": CURRENT_STATE["job_description"].to_dict() if CURRENT_STATE["job_description"] else None,
            "candidates": [c.to_dict() for c in CURRENT_STATE["candidates"]],
            "last_analyzed_at": CURRENT_STATE["last_analyzed_at"]
        }
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        app.logger.error(f"Failed to save session state: {e}")


def load_session_state():
    """Load session state from JSON file if it exists."""
    global CURRENT_STATE
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                jd_data = data.get("job_description")
                if jd_data:
                    CURRENT_STATE["job_description"] = JobDescription(**jd_data)
                else:
                    CURRENT_STATE["job_description"] = None

                cands_data = data.get("candidates", [])
                loaded_cands = []
                for cd in cands_data:
                    loaded_cands.append(Candidate.from_dict(cd))
                CURRENT_STATE["candidates"] = loaded_cands
                CURRENT_STATE["last_analyzed_at"] = data.get("last_analyzed_at")
        except Exception as e:
            app.logger.error(f"Failed to load session state: {e}")


# Initialize session state on startup
load_session_state()


def allowed_file(filename: str) -> bool:
    """Validate file extension against allowed types."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def compute_dashboard_stats() -> Dict[str, Any]:
    """Calculate aggregate metrics for the dashboard cards."""
    candidates = CURRENT_STATE["candidates"]
    total = len(candidates)
    screened = len([c for c in candidates if c.score_breakdown.overall_score > 0])
    shortlisted = len([c for c in candidates if c.is_shortlisted])
    
    if screened > 0:
        scores = [c.score_breakdown.overall_score for c in candidates if c.score_breakdown.overall_score > 0]
        top_match = max(scores)
        avg_score = round(sum(scores) / len(scores), 1)
    else:
        top_match = 0.0
        avg_score = 0.0

    return {
        "total_candidates": total,
        "screened_candidates": screened,
        "top_match_score": top_match,
        "avg_match_score": avg_score,
        "shortlisted_count": shortlisted
    }


# -------------------------------------------------------------
# HTML PAGE ROUTES
# -------------------------------------------------------------

@app.route("/")
def index():
    """Landing and ATS application entry point."""
    stats = compute_dashboard_stats()
    return render_template(
        "dashboard.html",
        stats=stats,
        jd=CURRENT_STATE["job_description"],
        candidates=CURRENT_STATE["candidates"]
    )


@app.route("/dashboard")
def dashboard():
    """Main recruiter dashboard."""
    stats = compute_dashboard_stats()
    return render_template(
        "dashboard.html",
        stats=stats,
        jd=CURRENT_STATE["job_description"],
        candidates=CURRENT_STATE["candidates"]
    )


@app.route("/results")
def results():
    """Candidate rankings table view."""
    stats = compute_dashboard_stats()
    return render_template(
        "results.html",
        stats=stats,
        jd=CURRENT_STATE["job_description"],
        candidates=CURRENT_STATE["candidates"]
    )


# -------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Return dashboard summary statistics."""
    return jsonify({"success": True, "stats": compute_dashboard_stats()})


@app.route("/api/sample-jds", methods=["GET"])
def list_sample_jds():
    """Return available sample Job Descriptions."""
    jds_dir = os.path.join(app.config["SAMPLES_FOLDER"], "sample_jds")
    samples = []
    if os.path.exists(jds_dir):
        for fname in os.listdir(jds_dir):
            if fname.endswith(".txt"):
                path = os.path.join(jds_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    title_line = content.split("\n")[0].replace("Job Title:", "").strip()
                    samples.append({
                        "id": fname,
                        "filename": fname,
                        "title": title_line or fname,
                        "content": content
                    })
    return jsonify({"success": True, "samples": samples})


@app.route("/api/parse-jd", methods=["POST"])
def parse_jd_preview():
    """Parse and return live extracted requirements from a JD string."""
    data = request.get_json() or {}
    jd_text = data.get("jd_text", "").strip()
    custom_title = data.get("jd_title", "").strip()
    if not jd_text:
        return jsonify({"success": False, "error": "No JD text provided"}), 400

    jd = NLPAnalyzer.parse_job_description(jd_text, custom_title=custom_title)
    return jsonify({"success": True, "job_description": jd.to_dict()})



@app.route("/api/upload-resumes", methods=["POST"])
def upload_resumes():
    """
    Handle multi-file resume uploads.
    Extracts text and initial profile information for each file.
    """
    if "files" not in request.files:
        return jsonify({"success": False, "error": "No file part in request"}), 400

    uploaded_files = request.files.getlist("files")
    if not uploaded_files or uploaded_files[0].filename == "":
        return jsonify({"success": False, "error": "No files selected"}), 400

    processed_candidates = []
    errors = []

    for file in uploaded_files:
        if not file or not file.filename:
            continue

        if not allowed_file(file.filename):
            errors.append(f"{file.filename}: Unsupported file format. Please upload PDF, DOCX, or TXT.")
            continue

        orig_filename = secure_filename(file.filename) or f"resume_{uuid.uuid4().hex[:8]}.pdf"
        unique_name = f"{uuid.uuid4().hex[:8]}_{orig_filename}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        
        try:
            file.save(save_path)
            # Parse resume
            candidate = ResumeParser.parse_resume(save_path, original_filename=orig_filename)
            processed_candidates.append(candidate)
        except Exception as e:
            errors.append(f"{orig_filename}: Extraction error ({str(e)})")

    # Append new candidates to state (avoiding duplicates based on filename)
    existing_filenames = {c.filename for c in CURRENT_STATE["candidates"]}
    for c in processed_candidates:
        if c.filename not in existing_filenames:
            CURRENT_STATE["candidates"].append(c)
        else:
            # Replace existing entry with fresh parse
            CURRENT_STATE["candidates"] = [existing for existing in CURRENT_STATE["candidates"] if existing.filename != c.filename]
            CURRENT_STATE["candidates"].append(c)

    save_session_state()

    return jsonify({
        "success": True,
        "message": f"Successfully uploaded and parsed {len(processed_candidates)} resumes.",
        "uploaded_count": len(processed_candidates),
        "total_candidates": len(CURRENT_STATE["candidates"]),
        "errors": errors
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_and_rank():
    """
    Run full NLP analysis pipeline and candidate ranking against a Job Description.
    """
    data = request.get_json() or {}
    jd_text = data.get("jd_text", "").strip()
    custom_title = data.get("jd_title", "").strip()

    if not jd_text and not CURRENT_STATE["job_description"]:
        return jsonify({"success": False, "error": "Please provide a Job Description to rank candidates."}), 400

    if not CURRENT_STATE["candidates"]:
        return jsonify({"success": False, "error": "No resumes uploaded to rank. Please upload resumes first."}), 400

    # Parse and update Job Description if new text provided
    if jd_text:
        jd = NLPAnalyzer.parse_job_description(jd_text, custom_title=custom_title)
        CURRENT_STATE["job_description"] = jd
    else:
        jd = CURRENT_STATE["job_description"]

    # Rank all candidates
    engine = RankingEngine()
    ranked_candidates = engine.rank_candidates(CURRENT_STATE["candidates"], jd)
    CURRENT_STATE["candidates"] = ranked_candidates
    CURRENT_STATE["last_analyzed_at"] = datetime.now().isoformat()

    save_session_state()

    return jsonify({
        "success": True,
        "message": f"Successfully screened and ranked {len(ranked_candidates)} candidates.",
        "job_description": jd.to_dict(),
        "candidates": [c.to_dict() for c in ranked_candidates],
        "stats": compute_dashboard_stats()
    })


@app.route("/api/candidates", methods=["GET"])
def get_candidates():
    """Return all current candidates and active job description."""
    return jsonify({
        "success": True,
        "candidates": [c.to_dict() for c in CURRENT_STATE["candidates"]],
        "job_description": CURRENT_STATE["job_description"].to_dict() if CURRENT_STATE["job_description"] else None,
        "stats": compute_dashboard_stats()
    })


@app.route("/api/candidate/<cand_id>", methods=["GET"])
def get_candidate_details(cand_id: str):
    """Return full detail profile of a specific candidate."""
    cand = next((c for c in CURRENT_STATE["candidates"] if c.id == cand_id), None)
    if not cand:
        return jsonify({"success": False, "error": "Candidate not found"}), 404

    return jsonify({
        "success": True,
        "candidate": cand.to_dict(),
        "job_description": CURRENT_STATE["job_description"].to_dict() if CURRENT_STATE["job_description"] else None
    })


@app.route("/api/candidate/<cand_id>/shortlist", methods=["POST"])
def toggle_shortlist(cand_id: str):
    """Toggle candidate shortlisted status."""
    cand = next((c for c in CURRENT_STATE["candidates"] if c.id == cand_id), None)
    if not cand:
        return jsonify({"success": False, "error": "Candidate not found"}), 404

    cand.is_shortlisted = not cand.is_shortlisted
    if cand.is_shortlisted and cand.status in ("New", "Screening"):
        cand.status = "Shortlisted"
    elif not cand.is_shortlisted and cand.status == "Shortlisted":
        cand.status = "Screening"

    save_session_state()
    return jsonify({
        "success": True,
        "is_shortlisted": cand.is_shortlisted,
        "status": cand.status,
        "stats": compute_dashboard_stats()
    })


@app.route("/api/candidate/<cand_id>/status", methods=["POST"])
def update_status(cand_id: str):
    """Update candidate recruitment lifecycle status."""
    cand = next((c for c in CURRENT_STATE["candidates"] if c.id == cand_id), None)
    if not cand:
        return jsonify({"success": False, "error": "Candidate not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status", "New")
    valid_statuses = {"New", "Screening", "Shortlisted", "Interview", "Rejected", "Hired"}
    if new_status not in valid_statuses:
        return jsonify({"success": False, "error": f"Invalid status. Must be one of {valid_statuses}"}), 400

    cand.status = new_status
    if new_status == "Shortlisted":
        cand.is_shortlisted = True
    elif new_status in ("Rejected", "New"):
        cand.is_shortlisted = False

    save_session_state()
    return jsonify({"success": True, "status": cand.status, "is_shortlisted": cand.is_shortlisted})


@app.route("/api/candidate/<cand_id>/notes", methods=["POST"])
def update_notes(cand_id: str):
    """Save recruiter notes for a candidate."""
    cand = next((c for c in CURRENT_STATE["candidates"] if c.id == cand_id), None)
    if not cand:
        return jsonify({"success": False, "error": "Candidate not found"}), 404

    data = request.get_json() or {}
    cand.notes = data.get("notes", "").strip()
    save_session_state()
    return jsonify({"success": True, "notes": cand.notes})


@app.route("/api/candidate/<cand_id>/file", methods=["GET"])
def view_resume_file(cand_id: str):
    """Serve the original uploaded resume document."""
    cand = next((c for c in CURRENT_STATE["candidates"] if c.id == cand_id), None)
    if not cand or not cand.filepath or not os.path.exists(cand.filepath):
        return jsonify({"success": False, "error": "File not found"}), 404

    as_attachment = request.args.get("download", "0") == "1"
    return send_file(
        cand.filepath,
        as_attachment=as_attachment,
        download_name=cand.filename
    )


@app.route("/api/load-sample", methods=["POST"])
def load_sample_dataset():
    """Load pre-bundled realistic sample resumes and JD for 1-click test."""
    data = request.get_json() or {}
    jd_type = data.get("jd_type", "senior_fullstack_engineer")
    
    # 1. Load JD
    jd_path = os.path.join(app.config["SAMPLES_FOLDER"], "sample_jds", f"{jd_type}.txt")
    if not os.path.exists(jd_path):
        jd_path = os.path.join(app.config["SAMPLES_FOLDER"], "sample_jds", "senior_fullstack_engineer.txt")
        
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    jd = NLPAnalyzer.parse_job_description(jd_text)
    CURRENT_STATE["job_description"] = jd

    # 2. Parse all sample resumes
    resumes_dir = os.path.join(app.config["SAMPLES_FOLDER"], "sample_resumes")
    candidates = []
    if os.path.exists(resumes_dir):
        for fname in os.listdir(resumes_dir):
            fpath = os.path.join(resumes_dir, fname)
            if os.path.isfile(fpath) and allowed_file(fname):
                # Copy file to uploads folder so it can be previewed/downloaded
                unique_name = f"sample_{fname}"
                dest_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
                shutil.copyfile(fpath, dest_path)
                
                cand = ResumeParser.parse_resume(dest_path, original_filename=fname)
                candidates.append(cand)

    # 3. Rank candidates against JD
    engine = RankingEngine()
    ranked = engine.rank_candidates(candidates, jd)
    CURRENT_STATE["candidates"] = ranked
    CURRENT_STATE["last_analyzed_at"] = datetime.now().isoformat()

    save_session_state()

    return jsonify({
        "success": True,
        "message": f"Successfully loaded sample JD ('{jd.title}') and {len(ranked)} sample resumes.",
        "job_description": jd.to_dict(),
        "candidates": [c.to_dict() for c in ranked],
        "stats": compute_dashboard_stats()
    })


@app.route("/api/reset", methods=["POST"])
def reset_session():
    """Clear current candidates and session data."""
    global CURRENT_STATE
    CURRENT_STATE = {
        "job_description": None,
        "candidates": [],
        "last_analyzed_at": None
    }
    if os.path.exists(RESULTS_FILE):
        try:
            os.remove(RESULTS_FILE)
        except Exception:
            pass
    return jsonify({"success": True, "message": "Session reset successfully.", "stats": compute_dashboard_stats()})


@app.route("/api/export", methods=["GET"])
def export_results():
    """Export ranked candidate list as CSV or JSON."""
    fmt = request.args.get("format", "csv").lower()
    candidates = CURRENT_STATE["candidates"]

    if fmt == "json":
        output = {
            "job_description": CURRENT_STATE["job_description"].to_dict() if CURRENT_STATE["job_description"] else None,
            "generated_at": datetime.now().isoformat(),
            "candidates": [c.to_dict() for c in candidates]
        }
        json_bytes = io.BytesIO(json.dumps(output, indent=2).encode("utf-8"))
        return send_file(
            json_bytes,
            mimetype="application/json",
            as_attachment=True,
            download_name=f"ats_candidate_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    # Default: CSV export
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow([
        "Rank",
        "Candidate Name",
        "Email",
        "Phone",
        "Overall Score (%)",
        "Skills Match (%)",
        "Experience Match (%)",
        "Education Match (%)",
        "JD Similarity (%)",
        "Recommendation",
        "Status",
        "Shortlisted",
        "Total Experience",
        "Highest Education",
        "Matched Skills",
        "Missing Skills",
        "Recruiter Notes"
    ])

    for c in candidates:
        writer.writerow([
            c.rank,
            c.name,
            c.email,
            c.phone,
            f"{c.score_breakdown.overall_score:.1f}",
            f"{c.score_breakdown.skills_score:.1f}",
            f"{c.score_breakdown.experience_score:.1f}",
            f"{c.score_breakdown.education_score:.1f}",
            f"{c.score_breakdown.similarity_score:.1f}",
            c.recommendation,
            c.status,
            "Yes" if c.is_shortlisted else "No",
            c.experience_text,
            c.education_level,
            "; ".join(c.matched_required_skills),
            "; ".join(c.missing_required_skills),
            c.notes
        ])

    mem = io.BytesIO(si.getvalue().encode("utf-8-sig"))
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"ats_candidate_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )


if __name__ == "__main__":
    print("=" * 60)
    print("  AI Resume Screening & Candidate Ranking System (ATS)")
    print("  Running locally on http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
