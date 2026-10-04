"""Task definition for explaining calculated job matches."""

from crewai import Agent, Task


def create_job_matching_task(agent: Agent, resume_task: Task) -> Task:
    """Create a task that explains scores calculated by the Python matcher."""
    return Task(
        description=(
            "Explain the supplied candidate/job matching results. These records and "
            "all numeric scores were calculated by the application; preserve them and "
            "do not create new scores. Explain semantic similarity and exact skill "
            "overlap separately, note that neither is hiring probability, and identify "
            "matching and missing skills. Label source_type sample_dataset as sample "
            "opportunities.\n\nTARGET ROLE: {target_role}\nMATCH RESULTS:\n{job_matches}"
        ),
        expected_output=(
            "A ranked, evidence-based explanation of suitable roles, key matches, "
            "skill gaps, and practical improvements."
        ),
        agent=agent,
        context=[resume_task],
    )
