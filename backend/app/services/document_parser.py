"""
Document Parser — extracts text from PDF, DOCX, and TXT files.
Handles multi-page PDFs, preserves page numbers for citation.
"""

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from pathlib import Path
import re


def parse_document(file_path: str) -> list[dict]:
    """
    Parse a document and return structured pages.
    
    Returns:
        List of dicts: [{"page": 1, "text": "..."}, {"page": 2, "text": "..."}, ...]
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(file_path)
    elif suffix == ".docx":
        return _parse_docx(file_path)
    elif suffix == ".txt":
        return _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _parse_pdf(file_path: str) -> list[dict]:
    """Extract text from each page of a PDF using PyMuPDF."""
    pages = []
    doc = fitz.open(file_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        cleaned = _clean_text(text)
        if cleaned.strip():
            pages.append({"page": page_num + 1, "text": cleaned})
    doc.close()
    return pages


def _parse_docx(file_path: str) -> list[dict]:
    """Extract text from a DOCX file. Treated as single page."""
    doc = DocxDocument(file_path)
    full_text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    cleaned = _clean_text(full_text)
    if cleaned.strip():
        return [{"page": 1, "text": cleaned}]
    return []


def _parse_txt(file_path: str) -> list[dict]:
    """Read a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    cleaned = _clean_text(text)
    if cleaned.strip():
        return [{"page": 1, "text": cleaned}]
    return []


def _clean_text(text: str) -> str:
    """
    Clean extracted text:
    - Fix broken hyphenation from PDF extraction
    - Remove page headers/footers patterns
    - Collapse excessive whitespace
    """
    # Fix hyphenated line breaks: "imple-\nmentation" → "implementation"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Remove standalone page numbers
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    # Collapse multiple newlines into double newline
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
