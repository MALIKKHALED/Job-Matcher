"""Crew task definitions."""

from crewai import Task
import os

from pipeline.agents import scraper_agent, resume_extractor_agent, ats_scorer_agent, resume_enhancer_agent
from pipeline.models import JobDetails, ResumeProfile, ATSReport, OptimizedResume

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

def enhance_resume_task(context: list | None = None) -> Task:
    return Task(
        description=(
            "You are the Resume Enhancer. In context you receive three previous task "
            "outputs: the scraped JobDetails, the structured ResumeProfile, and the "
            "ATSReport.\n\n"
            "Your job: produce an optimized resume as Markdown, plus a missing-info report.\n\n"
            "RULES -- NON-NEGOTIABLE:\n"
            "- Every claim in the optimized resume must be traceable to the ResumeProfile. "
            "Never introduce a skill, metric, company, degree, certification, or date "
            "that is not in the ResumeProfile.\n"
            "- You may rephrase (verb-led, active, consistent tense/formatting) and reorder "
            "sections within the resume's existing facts.\n"
            "- The Skills section may contain ONLY skills present in the ResumeProfile "
            "(verbatim, or a synonym ONLY when the capability is explicitly demonstrated "
            "by a bullet). Never import job keywords into the Skills section.\n"
            "- If a job keyword is absent from the resume, do not add it -- add a "
            "conditional suggestion to missing_info_report instead (e.g. \"If you have X, "
            "add it to skills\").\n"
            "- 'changes' must describe edits actually visible in the markdown. Do not "
            "claim reorderings or rewrites that are not present in the output.\n"
            "- If a section or field is missing, do NOT create it and do NOT fill it with "
            "placeholders -- add the item to missing_info_report instead.\n"
            "- Address the ATS deductions you legitimately can; leave the rest for the report.\n"
            "- For each change you make, add a one-line entry to 'changes' describing what "
            "you repackaged or aligned (no invented-fact changes allowed).\n\n"
            "If additional candidate-provided corrections are supplied in user_supplied_info, "
            "treat them as trusted facts and incorporate them (and note them in 'changes'); "
            "if it is empty, ignore it.\n"
            "user_supplied_info: {user_supplied_info}"
        ),
        expected_output=(
            "A JSON object matching the OptimizedResume schema: the full optimized resume "
            "in Markdown, a 'changes' list of safe restatements applied, and a "
            "missing_info_report checklist of what only the candidate can add."
        ),
        output_pydantic=OptimizedResume,
        output_file=os.path.join("ai_agent_output", "step_4_optimized_resume.json"),
        agent=resume_enhancer_agent(),
        context=context,
    )