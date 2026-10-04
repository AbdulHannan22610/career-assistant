"""Small, explainable text-cleaning and skill-extraction helpers."""

from __future__ import annotations

import re

KNOWN_SKILLS = (
    "python", "java", "javascript", "typescript", "c++", "sql", "html", "css",
    "react", "node.js", "django", "flask", "fastapi", "streamlit", "pandas",
    "numpy", "scikit-learn", "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "data analysis", "data visualization", "power bi",
    "tableau", "excel", "statistics", "git", "docker", "aws", "azure", "gcp",
    "rest api", "mongodb", "postgresql", "mysql", "linux", "communication",
    "teamwork", "leadership", "problem solving", "critical thinking",
)


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving meaningful line boundaries."""
    if not text:
        return ""
    text = text.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    cleaned: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = not line
        if is_blank and previous_blank:
            continue
        cleaned.append(line)
        previous_blank = is_blank
    return "\n".join(cleaned).strip()


def normalize_skill(skill: str) -> str:
    """Return a consistent lowercase representation of a skill."""
    return re.sub(r"\s+", " ", skill.strip().lower())


def extract_skills(text: str) -> list[str]:
    """Find known skill phrases in text without inventing related skills."""
    searchable_text = normalize_text(text).lower()
    found = []
    for skill in KNOWN_SKILLS:
        pattern = rf"(?<![\w+#.]){re.escape(skill)}(?![\w+#.])"
        if re.search(pattern, searchable_text):
            found.append(skill)
    return sorted(set(found))
