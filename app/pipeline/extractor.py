"""
Document text extraction module.
Supports PDF, TXT, and DOCX file formats.
"""

import io
from pathlib import Path


def extract_text(file_content: bytes, filename: str) -> str:
    """
    Extract raw text from a document file.
    
    Args:
        file_content: Raw bytes of the file.
        filename: Original filename (used to determine file type).
    
    Returns:
        Extracted text as a string.
    
    Raises:
        ValueError: If the file type is not supported.
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return _extract_from_pdf(file_content)
    elif suffix == ".txt":
        return _extract_from_txt(file_content)
    elif suffix in (".docx", ".doc"):
        return _extract_from_docx(file_content)
    else:
        raise ValueError(
            f"Unsupported file type: '{suffix}'. Supported types: .pdf, .txt, .docx"
        )


def _extract_from_pdf(content: bytes) -> str:
    """Extract text from a PDF file using PyPDF2."""
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(content))
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text.strip())
    
    full_text = "\n\n".join(pages_text)
    if not full_text.strip():
        raise ValueError("Could not extract any text from the PDF. It may be image-based.")
    return full_text


def _extract_from_txt(content: bytes) -> str:
    """Extract text from a plain text file."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")
    
    if not text.strip():
        raise ValueError("The text file is empty.")
    return text.strip()


def _extract_from_docx(content: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    from docx import Document

    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    full_text = "\n".join(paragraphs)
    if not full_text.strip():
        raise ValueError("Could not extract any text from the DOCX file.")
    return full_text
