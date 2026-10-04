"""Build and run the sequential four-agent CareerAssist workflow."""

from __future__ import annotations

import json
from typing import Any

from crewai import Crew, Process

from agents.career_guidance_agent import create_career_guidance_agent
from agents.interview_preparation_agent import create_interview_preparation_agent
from agents.job_matching_agent import create_job_matching_agent
from agents.resume_analyzer_agent import create_resume_analyzer_agent
from config.llm_config import create_llm
from tasks.career_guidance_task import create_career_guidance_task
from tasks.interview_preparation_task import create_interview_preparation_task
from tasks.job_matching_task import create_job_matching_task
from tasks.resume_analysis_task import create_resume_analysis_task


class CareerAssistCrew:
    """Coordinate analysis tasks while sharing one configured Groq LLM."""

    def __init__(self, llm: Any | None = None) -> None:
        shared_llm = llm or create_llm()
        resume_agent = create_resume_analyzer_agent(shared_llm)
        matching_agent = create_job_matching_agent(shared_llm)
        guidance_agent = create_career_guidance_agent(shared_llm)
        interview_agent = create_interview_preparation_agent(shared_llm)

        resume_task = create_resume_analysis_task(resume_agent)
        matching_task = create_job_matching_task(matching_agent, resume_task)
        guidance_task = create_career_guidance_task(
            guidance_agent, resume_task, matching_task
        )
        interview_task = create_interview_preparation_task(
            interview_agent, resume_task, matching_task, guidance_task
        )
        self.tasks = [resume_task, matching_task, guidance_task, interview_task]
        self.crew = Crew(
            agents=[resume_agent, matching_agent, guidance_agent, interview_agent],
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )

    def run(
        self,
        resume_text: str,
        job_matches: list[dict[str, Any]],
        preferred_field: str,
        target_role: str,
    ) -> dict[str, str]:
        """Run each specialist in sequence and return each task's written output."""
        result = self.crew.kickoff(
            inputs={
                "resume_text": resume_text,
                "job_matches": json.dumps(job_matches, ensure_ascii=False, indent=2),
                "preferred_field": preferred_field,
                "target_role": target_role,
            }
        )
        task_outputs = getattr(result, "tasks_output", []) or []
        output_names = (
            "resume_analysis",
            "job_matching",
            "career_guidance",
            "interview_preparation",
        )
        outputs = {
            name: str(getattr(task_output, "raw", task_output))
            for name, task_output in zip(output_names, task_outputs)
        }
        outputs.setdefault("interview_preparation", str(getattr(result, "raw", result)))
        return outputs
