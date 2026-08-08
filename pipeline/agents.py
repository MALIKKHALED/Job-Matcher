"""Crew agent definitions."""

from crewai import Agent

from app.core.config import build_llm
from pipeline.tools import scrape_job_page


def scraper_agent() -> Agent:
    return Agent(
        role="Scrape the Job Details",
        goal=(
            "Scrape the job posting and extract its exact keywords, required skills, "
            "qualifications, responsibilities, and company culture. Never invent "
            "information that is not on the page."
        ),
        backstory=(
            "You are a precise web scraper for job postings. You extract the "
            "company, job title, description, responsibilities, requirements, "
            "and any other facts exactly as they appear, and nothing more."
        ),
        llm=build_llm(),
        tools=[scrape_job_page],
        verbose=True,
        allow_delegation=False,
        memory=False,
    )