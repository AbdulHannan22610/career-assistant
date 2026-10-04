"""Lazy sentence-embedding matching with transparent skill-overlap scores."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from config.settings import get_settings
from tools.text_processor import extract_skills


@lru_cache(maxsize=1)
def load_embedding_model(model_name: str | None = None) -> Any:
    """Load and cache the configured embedding model only when matching runs."""
    from sentence_transformers import SentenceTransformer

    selected_model = model_name or get_settings().embedding_model
    return SentenceTransformer(selected_model)


def generate_embedding(text: str, model: Any | None = None) -> Any:
    """Generate an embedding for non-empty text using the shared model."""
    if not text or not text.strip():
        raise ValueError("Text is required to generate an embedding.")
    active_model = model or load_embedding_model()
    return active_model.encode([text], convert_to_numpy=True)[0]


def calculate_similarity(first_text: str, second_text: str, model: Any | None = None) -> float:
    """Return cosine similarity in the natural cosine range [-1, 1]."""
    if not first_text.strip() or not second_text.strip():
        raise ValueError("Both texts are required to calculate similarity.")
    from sklearn.metrics.pairwise import cosine_similarity

    active_model = model or load_embedding_model()
    embeddings = active_model.encode([first_text, second_text], convert_to_numpy=True)
    return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])


def match_resume_to_jobs(resume_text: str, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank jobs by semantic similarity and exact required-skill overlap.

    If model loading fails, jobs are still ranked by exact skill overlap and the
    returned semantic score stays null so the UI can disclose the limitation.
    """
    if not resume_text.strip():
        raise ValueError("Resume text is required for job matching.")
    if not jobs:
        return []

    candidate_skills = set(extract_skills(resume_text))
    semantic_scores: list[float] | None = None
    semantic_error: str | None = None
    try:
        model = load_embedding_model()
        texts = [resume_text] + [
            f"{job.get('job_title', '')}. {job.get('job_description', '')}. "
            f"Required skills: {job.get('required_skills', '')}. "
            f"Preferred skills: {job.get('preferred_skills', '')}"
            for job in jobs
        ]
        embeddings = model.encode(texts, convert_to_numpy=True)
        from sklearn.metrics.pairwise import cosine_similarity

        semantic_scores = cosine_similarity([embeddings[0]], embeddings[1:])[0].tolist()
    except Exception:
        semantic_error = "Semantic matching is temporarily unavailable; ranking uses exact skills only."

    results: list[dict[str, Any]] = []
    for index, job in enumerate(jobs):
        required = {
            skill.strip().lower()
            for skill in str(job.get("required_skills", "")).split(",")
            if skill.strip()
        }
        matched_skills = sorted(candidate_skills.intersection(required))
        missing_skills = sorted(required.difference(candidate_skills))
        overlap = len(matched_skills) / len(required) if required else 0.0
        semantic = max(0.0, min(1.0, float(semantic_scores[index]))) if semantic_scores is not None else None
        recommendation = (0.7 * semantic + 0.3 * overlap) if semantic is not None else overlap
        result = dict(job)
        result.update(
            {
                "semantic_similarity": semantic,
                "skill_overlap": overlap,
                "recommendation_score": recommendation,
                "matching_skills": matched_skills,
                "missing_skills": missing_skills,
            }
        )
        if semantic_error:
            result["matching_notice"] = semantic_error
        results.append(result)
    return sorted(results, key=lambda item: item["recommendation_score"], reverse=True)
