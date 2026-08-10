"""Pipeline orchestration: runs the crew and bundles structured results."""

import json
from dataclasses import asdict

from pydantic import BaseModel

from pipeline.ats_rubric import ATS_RUBRIC, MAX_ATS_SCORE
from pipeline.crew import build_pipeline
from pipeline.models import (
    ATSReport,
    CoverLetter,
    JobDetails,
    MatchReport,
    OptimizedResume,
    ResumeProfile,
)


class PipelineResult(BaseModel):
    job_details: JobDetails
    resume_profile: ResumeProfile
    ats_report: ATSReport
    optimized_resume: OptimizedResume
    match_report: MatchReport
    cover_letter: CoverLetter


def compute_recommendation(pct: int) -> str:
    if pct >= 70:
        return "Apply now"
    if pct >= 45:
        return "Improve then apply"
    return "Do not apply"


def run_pipeline(job_url: str, resume_text: str, user_supplied_info: str = "") -> PipelineResult:
    crew, tasks = build_pipeline()

    rubric_json = json.dumps([asdict(c) for c in ATS_RUBRIC], indent=2, ensure_ascii=False)
    crew.kickoff(inputs={
        "job_url": job_url,
        "resume_text": resume_text,
        "rubric": rubric_json,
        "max_ats_score": MAX_ATS_SCORE,
        "user_supplied_info": user_supplied_info,
    })

    job_details, resume_profile, ats_report, optimized_resume, match_report, cover_letter = [
        t.output.pydantic for t in tasks
    ]

    match_report.recommendation = compute_recommendation(match_report.match_percentage)

    return PipelineResult(
        job_details=job_details,
        resume_profile=resume_profile,
        ats_report=ats_report,
        optimized_resume=optimized_resume,
        match_report=match_report,
        cover_letter=cover_letter,
    )