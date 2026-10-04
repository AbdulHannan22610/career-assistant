"""Resume upload validation, extraction, and workflow entry point."""

from __future__ import annotations

from typing import Any

from tools.pdf_extractor import extract_pdf_text
from tools.text_processor import normalize_text
from utils.validators import validate_resume_text, validate_resume_upload

MAX_RESUME_CHARACTERS = 24_000


def prepare_resume(uploaded_file: Any) -> str:
    """Validate a PDF upload, extract its selectable text, and normalize it."""
    validate_resume_upload(uploaded_file)
    resume_text = normalize_text(extract_pdf_text(uploaded_file))
    validate_resume_text(resume_text)
    if len(resume_text) > MAX_RESUME_CHARACTERS:
        raise ValueError(
            f"The extracted resume is too long ({len(resume_text):,} characters). "
            f"Please use a shorter PDF (maximum {MAX_RESUME_CHARACTERS:,} characters)."
        )
    return resume_text


def run_resume_analysis(
    crew: Any,
    resume_text: str,
    job_matches: list[dict[str, Any]],
    preferred_field: str,
    target_role: str,
) -> dict[str, str]:
    """Delegate the validated resume and match context to the CrewAI workflow."""
    validate_resume_text(resume_text)
    return crew.run(resume_text, job_matches, preferred_field, target_role)
