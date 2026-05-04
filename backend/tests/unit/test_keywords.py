"""Test keyword extractor — hard skills, soft skills, alias resolution."""

from app.ml.keyword_extractor import extract_hard_skills, extract_soft_skills, extract_all_keywords
from app.ml.skill_graph import normalize_skill, expand_skills, get_implied_skills


def test_extract_hard_skills():
    text = "Experienced in Python, TensorFlow, and Docker"
    skills = extract_hard_skills(text)
    assert "python" in skills
    assert "tensorflow" in skills
    assert "docker" in skills


def test_extract_soft_skills():
    text = "Strong leadership and teamwork abilities with excellent communication"
    skills = extract_soft_skills(text)
    assert "leadership" in skills
    assert "teamwork" in skills
    assert "communication" in skills


def test_extract_all_keywords():
    text = "Python developer with machine learning experience and strong leadership"
    result = extract_all_keywords(text)
    assert "hard_skills" in result
    assert "soft_skills" in result
    assert "all_keywords" in result
    assert "python" in result["hard_skills"]
    assert "leadership" in result["soft_skills"]


def test_normalize_skill_aliases():
    assert normalize_skill("nodejs") == "node.js"
    assert normalize_skill("reactjs") == "react"
    assert normalize_skill("k8s") == "kubernetes"
    assert normalize_skill("sklearn") == "scikit-learn"
    assert normalize_skill("postgres") == "postgresql"


def test_normalize_skill_passthrough():
    assert normalize_skill("python") == "python"
    assert normalize_skill("unknown_skill") == "unknown_skill"


def test_get_implied_skills():
    implied = get_implied_skills("react")
    assert "javascript" in implied


def test_expand_skills():
    skills = {"react", "docker"}
    expanded = expand_skills(skills)
    assert "react" in expanded
    assert "javascript" in expanded  # implied by react
    assert "docker" in expanded
    assert "linux" in expanded  # implied by docker
