"""Task definition for role-specific interview preparation."""

from crewai import Agent, Task


def create_interview_preparation_task(
    agent: Agent, resume_task: Task, job_task: Task, guidance_task: Task
) -> Task:
    """Create interview practice from earlier analysis and the selected role."""
    return Task(
        description=(
            "Prepare candidate-specific interview practice for the target role "
            "({target_role}) and preferred field ({preferred_field}). Use only projects, "
            "skills, and experience supported by the resume context. Include technical, "
            "project/resume-based, and HR questions with answer guidance, plus concise "
            "preparation tips. Present suggested answers as drafts to personalize; do "
            "not invent candidate achievements."
        ),
        expected_output=(
            "A practical Markdown set of technical, resume/project, and HR questions "
            "with grounded answer guidance and interview tips."
        ),
        agent=agent,
        context=[resume_task, job_task, guidance_task],
    )
