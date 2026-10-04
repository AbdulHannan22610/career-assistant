"""CrewAI resume analysis specialist."""

from crewai import Agent


def create_resume_analyzer_agent(llm: object) -> Agent:
    """Create an agent that reports only evidence present in resume text."""
    return Agent(
        role="Professional Resume Analysis Specialist",
        goal=(
            "Accurately summarize a candidate's education, skills, projects, "
            "experience, certifications, strengths, and improvement areas."
        ),
        backstory=(
            "You are a careful resume reviewer. You distinguish explicit evidence "
            "from missing information and never invent qualifications or achievements."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
