"""Test section parser — section detection and text cleaning."""

from app.ml.section_parser import detect_sections, clean_text, validate_magic_bytes


def test_detect_sections():
    text = """John Doe
john@email.com

Summary
Experienced software engineer with 5 years of experience.

Experience
- Built microservices at Company A
- Led team of 5 engineers

Education
BS Computer Science, MIT 2018

Skills
Python, JavaScript, Docker, Kubernetes
"""
    sections = detect_sections(text)
    assert "summary" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "skills" in sections


def test_detect_sections_empty():
    sections = detect_sections("")
    assert isinstance(sections, dict)


def test_clean_text():
    text = "  Hello   World  \n\n  Test  "
    cleaned = clean_text(text)
    assert "  " not in cleaned
    assert cleaned == "Hello World Test"


def test_clean_text_bullets():
    text = "• Bullet one • Bullet two"
    cleaned = clean_text(text)
    assert "•" not in cleaned


def test_validate_magic_bytes_pdf():
    assert validate_magic_bytes(b"%PDF-1.4 content", ".pdf")
    assert not validate_magic_bytes(b"Not a PDF", ".pdf")


def test_validate_magic_bytes_docx():
    assert validate_magic_bytes(b"PK\x03\x04 content", ".docx")
    assert not validate_magic_bytes(b"Not a DOCX", ".docx")
