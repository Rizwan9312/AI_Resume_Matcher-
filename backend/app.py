import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from parser import parse_resume
from keywords import extract_all_keywords
from matcher import run_matching_pipeline
from rewriter import extract_bullets, rewrite_bullets, score_bullet_strength
# ── App Config ────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB limit
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Health Route ──────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# ─────────────────────────────────────────────────────────────
# 🚀 MAIN RESUME SCORING ROUTE
# ─────────────────────────────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No resume file provided"}), 400

        file = request.files["resume"]
        jd_text = request.form.get("job_description", "").strip()

        if file.filename == "":
            return jsonify({"error": "Empty file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF and DOCX allowed"}), 400

        if not jd_text:
            return jsonify({"error": "Job description required"}), 400

        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Step 1: Extract resume text
        resume_text = parse_resume(file_path)
        if not resume_text.strip():
            return jsonify({"error": "Could not extract resume text"}), 422

        # Step 2: Extract keywords
        resume_keywords = extract_all_keywords(resume_text)
        jd_keywords = extract_all_keywords(jd_text)

        # Step 3: Run ML matching pipeline
        result = run_matching_pipeline(
            resume_text=resume_text,
            jd_text=jd_text,
            resume_keywords=resume_keywords,
            jd_keywords=jd_keywords
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)

# ─────────────────────────────────────────────────────────────
# ✨ AI BULLET REWRITER ROUTE
# ─────────────────────────────────────────────────────────────
@app.route('/rewrite', methods=['POST'])
def rewrite():
    try:
        if "resume" not in request.files:
            return jsonify({"error": "No resume file provided"}), 400

        file = request.files["resume"]
        jd_text = request.form.get("job_description", "").strip()

        if file.filename == "":
            return jsonify({"error": "Empty file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF and DOCX allowed"}), 400

        if not jd_text:
            return jsonify({"error": "No job description provided"}), 400

        # Save resume
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Extract resume text
        resume_text = parse_resume(file_path)

        bullets = extract_bullets(resume_text)
        if not bullets:
            return jsonify({"error": "Could not extract bullet points"}), 400

        # Analyze strength
        strength_flags = [score_bullet_strength(b) for b in bullets]
        weak_count = sum(1 for f in strength_flags if f["needs_rewrite"])

        # Rewrite bullets
        rewrites = rewrite_bullets(bullets, jd_text)

        return jsonify({
            "rewrites": rewrites,
            "bullet_count": len(bullets),
            "weak_bullets": weak_count
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)

# ── Run Server ────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)