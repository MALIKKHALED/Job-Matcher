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