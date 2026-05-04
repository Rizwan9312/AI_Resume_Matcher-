"""Test TF-IDF scorer and file validation."""

from app.ml.tfidf_scorer import compute_tfidf_score
from app.utils.file_utils import validate_magic_bytes, validate_file_extension


def test_tfidf_similar_texts():
    resume = "Python developer with experience in machine learning and data analysis"
    jd = "Looking for a Python developer skilled in machine learning and data science"
    score = compute_tfidf_score(resume, jd)
    assert score > 30.0  # should be relatively similar


def test_tfidf_dissimilar_texts():
    resume = "Chef with 10 years cooking experience in French cuisine"
    jd = "Looking for a software engineer with kubernetes and docker"
    score = compute_tfidf_score(resume, jd)
    assert score < 20.0  # very different


def test_tfidf_empty_input():
    assert compute_tfidf_score("", "some text") == 0.0
    assert compute_tfidf_score("some text", "") == 0.0


def test_validate_magic_bytes_pdf():
    pdf_content = b"%PDF-1.4 some content here"
    assert validate_magic_bytes(pdf_content, ".pdf")
    assert not validate_magic_bytes(pdf_content, ".docx")


def test_validate_magic_bytes_docx():
    docx_content = b"PK\x03\x04 some zip content"
    assert validate_magic_bytes(docx_content, ".docx")
    assert not validate_magic_bytes(docx_content, ".pdf")


def test_validate_magic_bytes_invalid():
    assert not validate_magic_bytes(b"random bytes", ".pdf")
    assert not validate_magic_bytes(b"random bytes", ".docx")


def test_validate_file_extension():
    assert validate_file_extension("resume.pdf") == ".pdf"
    assert validate_file_extension("resume.docx") == ".docx"
    assert validate_file_extension("resume.txt") is None
    assert validate_file_extension("resume.exe") is None
