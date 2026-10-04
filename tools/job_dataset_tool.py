"""Load and filter the bundled illustrative job dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "job_id", "job_title", "company", "job_type", "experience_level", "location",
    "required_skills", "preferred_skills", "job_description", "application_url", "source_type",
}
DEFAULT_DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "jobs_dataset.csv"


class JobDatasetError(ValueError):
    """Raised when the job dataset is missing or does not match its schema."""


def load_jobs(path: str | Path | None = None) -> pd.DataFrame:
    """Read the CSV and verify that all required columns are present."""
    dataset_path = Path(path) if path else DEFAULT_DATASET_PATH
    if not dataset_path.is_file():
        raise JobDatasetError("The sample job dataset is missing from data/jobs_dataset.csv.")
    try:
        jobs = pd.read_csv(dataset_path).fillna("")
    except Exception as error:
        raise JobDatasetError("The job dataset could not be read as a CSV file.") from error
    missing = REQUIRED_COLUMNS.difference(jobs.columns)
    if missing:
        raise JobDatasetError("The job dataset is missing required columns: " + ", ".join(sorted(missing)))
    return jobs


def search_jobs(jobs: pd.DataFrame, title: str = "") -> pd.DataFrame:
    """Return rows whose job title contains the requested text."""
    if not title.strip():
        return jobs.copy()
    return jobs[jobs["job_title"].str.contains(title.strip(), case=False, na=False)].copy()


def filter_jobs(
    jobs: pd.DataFrame,
    job_type: str | None = None,
    location: str | None = None,
    experience_level: str | None = None,
) -> pd.DataFrame:
    """Apply optional, case-insensitive filters to job type, location, and level."""
    filtered = jobs.copy()
    for column, value in (
        ("job_type", job_type),
        ("location", location),
        ("experience_level", experience_level),
    ):
        if value and value != "All":
            filtered = filtered[filtered[column].str.contains(value, case=False, na=False)]
    return filtered.copy()


def job_records(jobs: pd.DataFrame) -> list[dict[str, str]]:
    """Convert dataset rows to plain dictionaries for matching and agent context."""
    return jobs.to_dict(orient="records")
