"""Combine agent outputs and deterministic match values into a download."""

from __future__ import annotations

from datetime import datetime
from typing import Any


SECTION_LABELS = (
    ("resume_analysis", "Resume Analysis"),
    ("job_matching", "Job Matching Explanation"),
    ("career_guidance", "Career Guidance"),
    ("interview_preparation", "Interview Preparation"),
)


def build_report(
    agent_outputs: dict[str, str],
    job_matches: list[dict[str, Any]],
    preferred_field: str,
    target_role: str,
) -> str:
    """Create a readable Markdown report with calculated scores and caveats."""
    sections = [
        "# CareerAssist Career Analysis",
        f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
        f"Preferred field: {preferred_field}",
        f"Target role: {target_role}",
        "",
        "> Sample-dataset roles are illustrative records, not verified live vacancies. "
        "Similarity is not a probability of getting hired.",
    ]
    for key, heading in SECTION_LABELS:
        sections.extend(["", f"## {heading}", agent_outputs.get(key, "This section was not generated.")])
    sections.extend(["", "## Calculated Job Scores"])
    if not job_matches:
        sections.append("No job records were available for comparison.")
    for job in job_matches:
        semantic = job.get("semantic_similarity")
        semantic_label = f"{float(semantic) * 100:.1f}%" if semantic is not None else "Unavailable"
        sections.extend(
            [
                "",
                f"### {job.get('job_title', 'Untitled role')} - {job.get('company', 'Unknown organization')}",
                f"- Source: {job.get('source_type', 'unknown')}",
                f"- Semantic similarity: {semantic_label}",
                f"- Exact required-skill overlap: {float(job.get('skill_overlap', 0)) * 100:.1f}%",
                f"- Combined recommendation score: {float(job.get('recommendation_score', 0)) * 100:.1f}%",
                f"- Matching skills: {', '.join(job.get('matching_skills', [])) or 'None identified'}",
                f"- Missing required skills: {', '.join(job.get('missing_skills', [])) or 'None identified'}",
            ]
        )
    return "\n".join(sections).strip() + "\n"
