"""Input validation helpers used by the application services."""

from __future__ import annotations

from typing import Any


def validate_resume_upload(uploaded_file: Any) -> None:
    """Raise a friendly error unless an upload is a non-empty PDF."""
    if uploaded_file is None:
        raise ValueError("Upload a PDF resume to continue.")
    filename = str(getattr(uploaded_file, "name", ""))
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Please select a PDF file. Other formats are not supported.")
    if getattr(uploaded_file, "size", 1) == 0:
        raise ValueError("The selected PDF is empty.")


def validate_resume_text(text: str) -> None:
    """Ensure extracted content contains text for analysis."""
    if not text or not text.strip():
        raise ValueError("No resume text was found. Please upload a text-based PDF.")
