"""
Extract plain text from a PDF given its raw bytes.
Uses PyMuPDF (fitz) — fast and dependency-light.
"""
import fitz  # PyMuPDF


def extract_text_from_pdf(raw_bytes: bytes) -> str:
    doc = fitz.open(stream=raw_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n".join(pages)