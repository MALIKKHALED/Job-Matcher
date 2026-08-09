class PipelineResult(BaseModel):
    job_details: JobDetails
    resume_profile: ResumeProfile
    ats_report: ATSReport
    optimized_resume: OptimizedResume
    match_report: MatchReport
    cover_letter: str = "N/A"

def run_pipeline(job_url: str, resume_text: str, user_supplied_info: str = "") -> PipelineResult:
    crew = build_crew()
    result = crew.kickoff(inputs={...})
    # read each task.output (pydantic) → build PipelineResult
    return PipelineResult(...)