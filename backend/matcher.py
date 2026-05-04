from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from role_score import apply_role_weights

# ── Lazy load model (safe + error-proof) ───────────────────────────────
_bert_model = None

def get_bert_model():
    global _bert_model
    if _bert_model is None:
        try:
            _bert_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            raise RuntimeError(f"BERT model load failed: {e}")
    return _bert_model


# ── TF-IDF Score ───────────────────────────────────────────────────────

def compute_tfidf_score(resume_text: str, jd_text: str) -> float:
    if not resume_text or not jd_text:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception:
        return 0.0


# ── BERT Score ─────────────────────────────────────────────────────────

def compute_bert_score(resume_text: str, jd_text: str) -> float:
    if not resume_text or not jd_text:
        return 0.0

    model = get_bert_model()

    try:
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        jd_embedding = model.encode(jd_text, convert_to_tensor=True)

        similarity = util.cos_sim(resume_embedding, jd_embedding)
        return round(float(similarity[0][0]) * 100, 2)

    except Exception:
        return 0.0


# ── Keyword Score ──────────────────────────────────────────────────────

def compute_keyword_score(resume_keywords, jd_keywords):
    resume_set = {kw.lower() for kw in resume_keywords}
    jd_set = {kw.lower() for kw in jd_keywords}

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)

    score = (len(matched) / len(jd_set) * 100) if jd_set else 0.0
    return round(score, 2), matched, missing


# ── Final Score ────────────────────────────────────────────────────────
 
def compute_final_score(bert_score, tfidf_score, keyword_score, job_description=""):
    role_result = apply_role_weights(
        bert_score,
        tfidf_score,
        keyword_score,
         job_description
    )

    return role_result["final_score"]
# ── Feedback ───────────────────────────────────────────────────────────

def generate_feedback(final_score, missing_keywords):
    if final_score >= 80:
        verdict = "Strong match! Your resume aligns well with this role."
    elif final_score >= 60:
        verdict = "Good match. A few improvements can help."
    elif final_score >= 40:
        verdict = "Moderate match. Tailor your resume more."
    else:
        verdict = "Low match. Significant improvements needed."

    if missing_keywords:
        verdict += " Missing skills: " + ", ".join(missing_keywords[:5])

    return verdict


# ── Pipeline ───────────────────────────────────────────────────────────

def run_matching_pipeline(resume_text, jd_text, resume_keywords, jd_keywords):
    bert_score = compute_bert_score(resume_text, jd_text)
    tfidf_score = compute_tfidf_score(resume_text, jd_text)

    keyword_score, matched_kws, missing_kws = compute_keyword_score(
        resume_keywords, jd_keywords
    )

    final_score = compute_final_score(bert_score, tfidf_score, keyword_score)
    feedback = generate_feedback(final_score, missing_kws)

    return {
        "bert_score": bert_score,
        "tfidf_score": tfidf_score,
        "keyword_score": keyword_score,
        "final_score": final_score,
        "feedback": feedback,
        "matched_keywords": matched_kws,
        "missing_keywords": missing_kws,
    }