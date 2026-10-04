"""Extract selectable text from PDF resumes uploaded to Streamlit."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from pypdf import PdfReader

from tools.text_processor import normalize_text


class ResumeExtractionError(ValueError):
    """Raised when an uploaded file cannot be read as a text-based PDF."""


def extract_pdf_text(uploaded_file: Any) -> str:
    """Extract and normalize text page by page from a PDF upload.

    OCR is intentionally not included. A scanned PDF without a text layer needs
    OCR software before its contents can be analyzed.
    """
    filename = str(getattr(uploaded_file, "name", "resume.pdf"))
    content_type = getattr(uploaded_file, "type", None)
    if not filename.lower().endswith(".pdf") or content_type not in (None, "", "application/pdf"):
        raise ResumeExtractionError("Please upload a PDF file. Other formats are not supported.")

    try:
        if hasattr(uploaded_file, "getvalue"):
            file_bytes = uploaded_file.getvalue()
        else:
            file_bytes = uploaded_file.read()
        if not file_bytes:
            raise ResumeExtractionError("The uploaded PDF is empty.")
        reader = PdfReader(BytesIO(file_bytes))
        if reader.is_encrypted:
            raise ResumeExtractionError("This PDF is password-protected. Please upload an unlocked copy.")
        pages = [page.extract_text() or "" for page in reader.pages]
    except ResumeExtractionError:
        raise
    except Exception as error:
        raise ResumeExtractionError(
            "The PDF could not be read. Confirm it is a valid, unlocked PDF and try again."
        ) from error

    text = normalize_text("\n".join(pages))
    if not text:
        raise ResumeExtractionError(
            "No selectable text was found. This may be a scanned PDF; OCR is not included, "
            "so please upload a text-based PDF."
        )
    return text
