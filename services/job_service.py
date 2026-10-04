"""Prepare candidate/job comparisons using the sample CSV and semantic matcher."""

from __future__ import annotations

from typing import Any

from tools.job_dataset_tool import JobDatasetError, filter_jobs, job_records, load_jobs, search_jobs
from tools.semantic_matcher import match_resume_to_jobs
from tools.text_processor import extract_skills


def prepare_job_matches(
    resume_text: str,
    target_role: str,
    custom_job_description: str = "",
    job_type: str | None = None,
    location: str | None = None,
    experience_level: str | None = None,
    limit: int = 8,
) -> tuple[list[dict[str, Any]], str | None]:
    """Return ranked job records and a non-sensitive dataset status message."""
    records: list[dict[str, Any]] = []
    dataset_notice: str | None = None
    try:
        dataset = load_jobs()
        filtered = filter_jobs(dataset, job_type, location, experience_level)
        if target_role and target_role != "Any role":
            role_matches = search_jobs(filtered, target_role)
            if not role_matches.empty:
                filtered = role_matches
        records = job_records(filtered)
    except JobDatasetError as error:
        dataset_notice = str(error)

    if custom_job_description.strip():
        custom_skills = extract_skills(custom_job_description)
        records.insert(
            0,
            {
                "job_id": "custom-description",
                "job_title": target_role if target_role != "Any role" else "Custom job description",
                "company": "User-provided description",
                "job_type": "Custom",
                "experience_level": "User supplied",
                "location": "Not specified",
                "required_skills": ", ".join(custom_skills),
                "preferred_skills": "",
                "job_description": custom_job_description.strip(),
                "application_url": "",
                "source_type": "user_provided_description",
            },
        )

    if not records:
        return [], dataset_notice or "No jobs match the selected filters."
    matches = match_resume_to_jobs(resume_text, records)
    return matches[:limit], dataset_notice
