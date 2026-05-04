"""Test role detector — role detection and final score computation."""

from app.ml.role_detector import detect_role, compute_final_score, apply_role_weights, ROLE_PROFILES


def test_detect_tech_role():
    jd = "Looking for a software engineer with python, javascript, and docker experience"
    role_key, profile = detect_role(jd)
    assert role_key == "tech"
    assert profile["label"] == "Technology / Engineering"


def test_detect_marketing_role():
    jd = "Digital marketing manager for SEO, social media campaigns, and brand growth"
    role_key, profile = detect_role(jd)
    assert role_key == "marketing"


def test_detect_general_fallback():
    jd = "We need someone enthusiastic and hardworking"
    role_key, profile = detect_role(jd)
    assert role_key == "general"
    assert profile["label"] == "General"


def test_detect_legal_role():
    jd = "Attorney needed for litigation, compliance, and regulatory matters. GDPR experience required."
    role_key, profile = detect_role(jd)
    assert role_key == "legal"


def test_detect_operations_role():
    jd = "Operations manager for supply chain, logistics, procurement and inventory management"
    role_key, profile = detect_role(jd)
    assert role_key == "operations"


def test_all_10_profiles_exist():
    expected = {"tech", "marketing", "finance", "product", "design", "sales", "hr", "data", "legal", "operations"}
    assert set(ROLE_PROFILES.keys()) == expected


def test_compute_final_score_3score():
    weights = {"bert": 0.45, "tfidf": 0.35, "keyword": 0.20}
    score = compute_final_score(80.0, 70.0, 60.0, None, weights)
    expected = 80.0 * 0.45 + 70.0 * 0.35 + 60.0 * 0.20
    assert score == round(expected, 1)


def test_compute_final_score_4score_with_llm():
    weights = {"bert": 0.45, "tfidf": 0.35, "keyword": 0.20}
    score = compute_final_score(80.0, 70.0, 60.0, 75.0, weights)
    assert 0.0 <= score <= 100.0


def test_compute_final_score_bounds():
    weights = {"bert": 0.50, "tfidf": 0.30, "keyword": 0.20}
    assert compute_final_score(0.0, 0.0, 0.0, None, weights) == 0.0
    assert compute_final_score(100.0, 100.0, 100.0, None, weights) == 100.0


def test_apply_role_weights():
    result = apply_role_weights(80.0, 70.0, 60.0, "python developer docker kubernetes")
    assert "final_score" in result
    assert "role_key" in result
    assert "role_label" in result
    assert "weights_used" in result
    assert "score_breakdown" in result
    assert result["role_key"] == "tech"
