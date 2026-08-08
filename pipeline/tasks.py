"""Crew task definitions."""

from crewai import Task
import os

from pipeline.agents import scraper_agent
from pipeline.models import JobDetails


def scrape_job_task() -> Task:
    return Task(
        description=(
            "Use the ScrapeJobPage tool to scrape the job posting at {job_url}. "
            "Extract every keyword, required skill, qualification, responsibility, "
            "and detail about company culture exactly as stated in the posting. "
            "Do not invent anything."
        ),
        expected_output=(
            "A JSON object containing JobDetails structure with all fields filled from the posting, "
        ),
        output_pydantic=JobDetails,
        output_file=os.path.join("ai_agent_output", "step_1_scraped_results.json"),
        agent=scraper_agent(),
    )