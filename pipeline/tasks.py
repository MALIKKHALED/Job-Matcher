"""Crew task definitions."""

from crewai import Task
import os

from pipeline.agents import scraper_agent, resume_extractor_agent, ats_scorer_agent
from pipeline.models import JobDetails, ResumeProfile, ATSReport

MAX_ATS_SCORE = 100

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

def extract_resume_task() -> Task:
    return Task(
        description=(
            "Parse the candidate resume text below and extract every fact into a "
            "structured ResumeProfile. Keep bullet points exactly as written; do not "
            "summarize or rewrite them. If a section is missing from the resume, do "
            "NOT invent it -- leave the field empty and add the section name to "
            "missing_sections.\n\n"
            "Resume text:\n{resume_text}"
        ),
        expected_output=(
            "A JSON object matching the ResumeProfile schema, with all present resume "
            "facts captured and absent sections listed in missing_sections."
        ),
        output_pydantic=ResumeProfile,
        output_file=os.path.join("ai_agent_output", "step_2_resume_profile.json"),
        agent=resume_extractor_agent(),
    )

def ats_score_task(context: list | None = None) -> Task:
    return Task(
        description=(
            "You are an ATS scoring judge. Score the candidate's structured resume "
            "profile (from the previous task's context) against the fixed rubric below. "
            "Apply exactly these criteria and weights -- do not invent criteria, change "
            "weights, or give partial credit beyond the rubric.\n\n"
            "RUBRIC (max {max_ats_score} points):\n{rubric}\n\n"
            "Rules:\n"
            "- For each criterion, award the full points only if the resume fully "
            "satisfies it; otherwise award 0.\n"
            "- 'Quantified achievements' requires actual numbers/percentages in the "
            "experience bullets.\n"
            "- The sum of points_earned across criteria must equal total_score.\n"
            "- Keep the resume data exactly as given; do not alter it."
        ),
        expected_output=(
            "A JSON object matching the ATSReport schema: total_score, max_score, one "
            "criteria entry per rubric item (criterion_id, category, points_earned, "
            "points_max, reason), strengths, deductions, and critical_missing."
        ),
        output_pydantic=ATSReport,
        output_file=os.path.join("ai_agent_output", "step_3_ats_report.json"),
        agent=ats_scorer_agent(),
        context=context,
    )