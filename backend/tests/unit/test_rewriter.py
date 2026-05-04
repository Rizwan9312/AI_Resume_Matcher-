"""Test rewriter — bullet extraction and strength scoring."""

from app.workers.rewrite_tasks import extract_bullets, score_bullet_strength


def test_extract_bullets():
    text = """Experience
- Led a team of 5 engineers to deliver microservices platform
- Responsible for writing documentation
• Increased test coverage from 40% to 95%
* Helped with code reviews
"""
    bullets = extract_bullets(text)
    assert len(bullets) >= 3


def test_extract_bullets_empty():
    assert extract_bullets("No bullets here just plain text") == []


def test_score_bullet_strong():
    result = score_bullet_strength("Increased revenue by 45% through automated pipeline optimization")
    assert not result["needs_rewrite"]
    assert "looks strong" in result["reason"]


def test_score_bullet_weak_starter():
    result = score_bullet_strength("Responsible for managing the team")
    assert result["needs_rewrite"]
    assert "weak" in result["reason"]


def test_score_bullet_no_metrics():
    result = score_bullet_strength("Managed cloud infrastructure deployments")
    assert result["needs_rewrite"]
    assert "metrics" in result["reason"]
