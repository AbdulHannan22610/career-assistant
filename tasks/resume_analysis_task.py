"""Task definition for resume evidence extraction and review."""

from crewai import Agent, Task


def create_resume_analysis_task(agent: Agent) -> Task:
    """Create the first task in the career analysis sequence."""
    return Task(
        description=(
            "Analyze the resume text below. Report a concise summary and separate "
            "sections for education, technical skills, soft skills, projects, experience, "
            "certifications, strengths, weaknesses, and specific improvements. State "
            "'Not found in the resume' when evidence is absent. Do not infer facts.\n\n"
            "RESUME TEXT:\n{resume_text}"
        ),
        expected_output=(
            "A structured Markdown report with the requested sections, grounded only "
            "in the supplied resume text."
        ),
        agent=agent,
    )
