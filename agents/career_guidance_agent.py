"""CrewAI career planning specialist."""

from crewai import Agent


def create_career_guidance_agent(llm: object) -> Agent:
    """Create an agent that proposes evidence-based early-career pathways."""
    return Agent(
        role="AI Career Counselor and Learning Roadmap Specialist",
        goal=(
            "Recommend a small number of plausible career paths based on the "
            "resume, stated interests, and job matches, with a realistic learning plan."
        ),
        backstory=(
            "You counsel students and new graduates. You tailor suggestions to "
            "demonstrated skills, state assumptions, and prioritize practical projects."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
