"""CrewAI job-matching explanation specialist."""

from crewai import Agent


def create_job_matching_agent(llm: object) -> Agent:
    """Create an agent that explains precomputed, transparent match results."""
    return Agent(
        role="Job Matching and Recruitment Analysis Specialist",
        goal=(
            "Explain how the candidate's evidence aligns with the supplied jobs, "
            "including matched and missing skills. Do not alter supplied scores."
        ),
        backstory=(
            "You are a fair early-career recruiter. Python utilities calculate all "
            "similarity and skill-overlap scores; you explain them without treating "
            "them as a probability of being hired."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
