"""Pydantic schemas for structured agent outputs."""

from pydantic import BaseModel, Field


class JobDetails(BaseModel):
    """Structured job posting details extracted by the scraper agent."""

    page_url: str = Field(default="N/A", title="Page URL")

    company_name: str = Field(default="N/A", title="Company Name")
    company_about: str = Field(default="N/A", title="Company About")
    company_culture: str = Field(default="N/A", title="Company Culture and Values")

    job_title: str = Field(default="N/A", title="Job Title")
    job_description: str = Field(default="N/A", title="Job Description")
    job_responsibilities: str = Field(default="N/A", title="Key Responsibilities")
    job_requirements: str = Field(default="N/A", title="Requirements, Required Skills and Qualifications")

    required_skills: list[str] = Field(default_factory=list, title="Required technical and soft skills")

    additional_notes: str = Field(default="N/A", title="Any Additional Note or important information")

class ExperienceItem(BaseModel):
    """A single work experience entry."""

    company: str = Field(default="", title="Company name")
    title: str = Field(default="", title="Job title / role")
    start_date: str = Field(default="", title="Start date")
    end_date: str = Field(default="", title="End date")
    bullets: list[str] = Field(default_factory=list, title="Achievement bullets as written")


class EducationItem(BaseModel):
    """A single education entry."""

    institution: str = Field(default="", title="Institution name")
    degree: str = Field(default="", title="Degree obtained")
    field: str = Field(default="", title="Field of study")
    start_date: str = Field(default="", title="Start date")
    end_date: str = Field(default="", title="End date")


class ResumeProfile(BaseModel):
    """Structured resume profile extracted by the resume extractor agent."""

    name: str = Field(default="", title="Full name")
    email: str = Field(default="", title="Email address")
    phone: str = Field(default="", title="Phone number")
    location: str = Field(default="", title="City, country or region")
    linkedin: str = Field(default="", title="LinkedIn or portfolio URL")
    summary: str = Field(default="", title="Professional summary")
    skills: list[str] = Field(default_factory=list, title="Skills listed on the resume")
    experience: list[ExperienceItem] = Field(default_factory=list, title="Work experience")
    education: list[EducationItem] = Field(default_factory=list, title="Education")
    certifications: list[str] = Field(default_factory=list, title="Certifications and licenses")
    missing_sections: list[str] = Field(default_factory=list, title="Sections absent from the resume")


class CriterionResult(BaseModel):
    """Score for a single rubric criterion."""

    criterion_id: str = Field(title="Rubric criterion id")
    category: str = Field(title="Criterion name")
    points_earned: int = Field(title="Points awarded")
    points_max: int = Field(title="Maximum points for this criterion")
    reason: str = Field(title="One-line justification")


class ATSReport(BaseModel):
    """ATS compliance report produced by the ATS scoring agent."""

    total_score: int = Field(title="Total ATS score out of max_score")
    max_score: int = Field(default=100, title="Maximum possible score")
    criteria: list[CriterionResult] = Field(default_factory=list, title="Per-criterion results")
    strengths: list[str] = Field(default_factory=list, title="What the resume does well")
    deductions: list[str] = Field(default_factory=list, title="What lost points and why")
    critical_missing: list[str] = Field(default_factory=list, title="Must-add checklist for the enhancer")

class OptimizedResume(BaseModel):
    """Repackaged resume (no invented facts) + report of what only the user can add."""

    markdown: str = Field(title="Full optimized resume in Markdown, built only from existing ResumeProfile facts")
    changes: list[str] = Field(default_factory=list, title="Safe restatements / alignments applied, for transparency")
    missing_info_report: list[str] = Field(default_factory=list, title="Actionable checklist of what the user must add") 

class MatchReport(BaseModel):
    """Job-specific match evaluation between the optimized resume and the job posting."""

    match_percentage: int = Field(title="Overall match percentage (0-100)")
    matched_skills: list[str] = Field(default_factory=list, title="Job skills demonstrably covered by the resume")
    missing_skills: list[str] = Field(default_factory=list, title="Job skills genuinely absent from the resume")
    strengths: list[str] = Field(default_factory=list, title="Strong alignment points")
    gaps: list[str] = Field(default_factory=list, title="Concrete weaknesses vs the posting")
    recommendation: str = Field(default="N/A", title="Apply now / Improve then apply / Do not apply") 

class CoverLetter(BaseModel):
    """Personalized cover letter grounded in the resume and job posting."""

    subject: str = Field(default="N/A", title="Email subject line")
    body: str = Field(default="N/A", title="Cover letter body in Markdown")
    notes: list[str] = Field(default_factory=list, title="Caveats for the user (e.g. verify facts before sending)")  