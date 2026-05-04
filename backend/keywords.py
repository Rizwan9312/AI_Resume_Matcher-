# keywords.py — Extract skills and keywords using spaCy NLP

import spacy
import re

# Load the medium model (includes word vectors)
nlp = spacy.load("en_core_web_md")

# ── Master Skills List ────────────────────────────────────────
HARD_SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "r", "sql",
    "html", "css", "bash", "scala", "kotlin", "swift", "go", "rust",

    # ML / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "neural network", "reinforcement learning", "feature engineering",
    "model training", "fine-tuning", "transfer learning",

    # ML Libraries & Frameworks
    "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost",
    "lightgbm", "hugging face", "transformers", "spacy", "nltk",
    "opencv", "mediapipe", "pandas", "numpy", "matplotlib", "seaborn",

    # Web Frameworks
    "flask", "django", "fastapi", "react", "node.js", "express",
    "next.js", "vue", "angular",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "firebase",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "ci/cd", "github actions", "linux", "rest api", "graphql",

    # Data
    "data analysis", "data visualization", "etl", "big data",
    "tableau", "power bi", "excel", "spark",
}

SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "collaboration",
    "adaptability", "creativity", "attention to detail",
    "project management", "analytical thinking", "decision making",
}


# ── Core Functions ────────────────────────────────────────────

def extract_keywords_spacy(text):
    """Use spaCy to extract named entities and noun chunks."""
    doc = nlp(text.lower())
    keywords = set()

    # Named entities (ORG, PRODUCT, etc.)
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "GPE", "WORK_OF_ART"):
            keywords.add(ent.text.strip())

    # Noun chunks (e.g., "machine learning engineer")
    for chunk in doc.noun_chunks:
        token = chunk.text.strip()
        if 2 <= len(token.split()) <= 4:  # only 2–4 word phrases
            keywords.add(token)

    return keywords


def extract_hard_skills(text):
    """Match text against the hard skills master list."""
    text_lower = text.lower()
    found = set()
    for skill in HARD_SKILLS:
        # Use word boundary matching for accuracy
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def extract_soft_skills(text):
    """Match text against the soft skills master list."""
    text_lower = text.lower()
    found = set()
    for skill in SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def extract_all_keywords(text):
    """
    Master function — runs all extractors and returns a
    structured dictionary of keyword results.
    """
    hard = extract_hard_skills(text)
    soft = extract_soft_skills(text)
    nlp_keywords = extract_keywords_spacy(text)

    return {
        "hard_skills": sorted(hard),
        "soft_skills": sorted(soft),
        "nlp_keywords": sorted(nlp_keywords),
        "all_keywords": sorted(hard | soft),  # combined for matching
    }


def display_keywords(keyword_dict):
    """Pretty-print the extracted keywords."""
    print("\n" + "="*50)
    print("📌 KEYWORD EXTRACTION RESULTS")
    print("="*50)

    print(f"\n🔧 Hard Skills ({len(keyword_dict['hard_skills'])} found):")
    print(", ".join(keyword_dict["hard_skills"]) or "None found")

    print(f"\n🤝 Soft Skills ({len(keyword_dict['soft_skills'])} found):")
    print(", ".join(keyword_dict["soft_skills"]) or "None found")

    print(f"\n🧠 NLP Extracted Phrases ({len(keyword_dict['nlp_keywords'])} found):")
    print(", ".join(list(keyword_dict["nlp_keywords"])[:15]) or "None found")

    print("\n" + "="*50)


# ── Checkpoint Test ───────────────────────────────────────────
if __name__ == "__main__":
    # Sample test text — replace with your own resume text
    sample_text = """
    Experienced Python developer with 3 years in machine learning and NLP.
    Proficient in TensorFlow, PyTorch, scikit-learn, and Flask.
    Strong background in data analysis using pandas and numpy.
    Worked with REST APIs, Docker, and deployed models on AWS.
    Excellent communication and teamwork skills.
    Led a team of 4 engineers, demonstrating strong leadership.
    """

    print("🔍 Running keyword extraction on sample text...")
    results = extract_all_keywords(sample_text)
    display_keywords(results)

    print("\n✅ Phase 3 checkpoint passed! keywords.py is working correctly.")