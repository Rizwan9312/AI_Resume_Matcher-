# parser.py — Extract text from PDF and DOCX resume files

import PyPDF2
import docx
import re
import os


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text


def clean_text(text):
    """Remove noise, extra spaces, and special characters."""
    text = re.sub(r'\s+', ' ', text)          # collapse whitespace
    text = re.sub(r'[^\x00-\x7F]+', ' ', text) # remove non-ASCII
    text = re.sub(r'[•●◆▪–—]', ' ', text)     # remove bullet symbols
    text = text.strip()
    return text


def parse_resume(file_path):
    """Main function — detect file type and extract clean text."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return ""

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file type: {ext}")
        return ""

    return clean_text(raw_text)


# ── Checkpoint test ──────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parser.py <resume_file.pdf or .docx>")
        sys.exit(1)

    file = sys.argv[1]
    result = parse_resume(file)

    if result:
        print("\n✅ Extracted Text (first 500 chars):\n")
        print(result[:500])
        print(f"\n📊 Total characters extracted: {len(result)}")
    else:
        print("❌ No text extracted. Check the file and try again.") 