"""Task definition for personalized career guidance and learning plans."""

from crewai import Agent, Task


def create_career_guidance_task(agent: Agent, resume_task: Task, job_task: Task) -> Task:
    """Create the career guidance task using resume and matching context."""
    return Task(
        description=(
            "Use the resume review and job matching context to recommend no more "
            "than three realistic career paths. Explain the evidence for each, list "
            "skills to develop, create a staged learning roadmap, suggest portfolio "
            "projects, and give practical next steps. Respect the user's preferred "
            "field ({preferred_field}) and target role ({target_role}) without forcing "
            "a poor fit. Do not claim unverified qualifications."
        ),
        expected_output=(
            "A personalized Markdown career plan containing career paths, rationale, "
            "skill gaps, a staged roadmap, portfolio projects, and next steps."
        ),
        agent=agent,
        context=[resume_task, job_task],
    )
