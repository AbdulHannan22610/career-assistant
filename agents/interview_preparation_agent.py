"""CrewAI interview preparation specialist."""

from crewai import Agent


def create_interview_preparation_agent(llm: object) -> Agent:
    """Create an agent that prepares resume- and role-specific questions."""
    return Agent(
        role="Technical Interview and HR Interview Preparation Specialist",
        goal=(
            "Prepare relevant technical, behavioral, and resume-based interview "
            "questions with grounded sample answer guidance and practical tips."
        ),
        backstory=(
            "You coach early-career candidates. You reference the candidate's actual "
            "projects and skills, avoid unsupported claims, and label answer examples "
            "as drafts the candidate should personalize."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
