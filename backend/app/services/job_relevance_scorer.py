"""Job relevance scorer — TF-IDF cosine similarity between resume and job descriptions."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


def score_jobs_against_resume(resume_text: str, jobs: List[Dict]) -> List[Dict]:
    """
    Scores each job's description against the resume using TF-IDF cosine similarity.
    Adds 'relevance_score' (0-100) to each job dict.
    Returns the list sorted highest score first.
    """
    if not jobs:
        return jobs

    job_descriptions = [j.get("job_description", "") or "" for j in jobs]
    corpus = [resume_text] + job_descriptions

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        resume_vec = tfidf_matrix[0]
        job_vecs   = tfidf_matrix[1:]
        similarities = cosine_similarity(resume_vec, job_vecs)[0]

        for i, job in enumerate(jobs):
            job["relevance_score"] = round(float(similarities[i]) * 100, 1)
    except Exception:
        for job in jobs:
            job["relevance_score"] = 0.0

    return sorted(jobs, key=lambda x: x["relevance_score"], reverse=True)
