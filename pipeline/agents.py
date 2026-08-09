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

def resume_extractor_agent() -> Agent:
    return Agent(
        role="Extract the Resume into Structured Data",
        goal=(
            "Extract every fact from the candidate's resume into a structured "
            "ResumeProfile: contact info, summary, skills, experience (with "
            "achievement bullets), education, certifications, and languages. "
            "Never invent, infer, or fill missing values."
        ),
        backstory=(
            "You are a meticulous resume parser. You convert a raw resume document "
            "into clean structured data. If a value is absent from the document you "
            "leave it empty and record the section name in missing_sections instead "
            "of guessing."
        ),
        llm=build_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )

def ats_scorer_agent() -> Agent:
    return Agent(
        role="ATS Compliance Judge",
        goal=(
            "Score the candidate's structured resume against the fixed ATS rubric, "
            "applying each criterion and weight exactly as given. Be strict and "
            "objective: award points only for what is verifiably present."
        ),
        backstory=(
            "You are an impartial ATS scoring system used by recruiters to filter "
            "resumes. You apply a fixed rubric and never show favoritism. If a resume "
            "lacks something, you deduct the full points for that criterion."
        ),
        llm=build_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )

def resume_enhancer_agent() -> Agent:
    return Agent(
        role="Resume Enhancer",
        goal=(
            "Repackage the candidate's resume within its own facts: improve phrasing, "
            "tone, ordering, and alignment with the job posting's keywords -- without "
            "ever inventing information. Produce a clean optimized resume plus a "
            "missing-info report of everything only the candidate can add."
        ),
        backstory=(
            "You are a meticulous resume editor who never fabricates. Every claim you "
            "write must be traceable to the candidate's ResumeProfile. You repurpose "
            "existing achievements into stronger, job-aligned language and clearly "
            "flag what is absent rather than filling gaps with inventions."
        ),
        llm=build_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )