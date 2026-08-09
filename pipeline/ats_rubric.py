"""Static ATS rubric. Single source of truth for ATS scoring."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ATSCriterion:
    id: str
    category: str
    points: int
    description: str
    missing_reason: str


ATS_RUBRIC: list[ATSCriterion] = [
    ATSCriterion("email", "Contact info", 4,
                 "Email.",
                 "No contact info found (email)"),
    ATSCriterion("phone", "Contact info", 4,
                     "phone.",
                     "No contact info found (phone)"),
    ATSCriterion("location", "Contact info", 2,
                     "location are present.",
                     "No contact info found (location)"),                              
    ATSCriterion("summary", "Professional summary", 10,
                 "A professional summary section exists.",
                 "No professional summary section"),
    ATSCriterion("experience", "Experience section", 15,
                 "Work experience present with company, title, and dates.",
                 "No work experience section"),
    ATSCriterion("education", "Education section", 15,
                 "Education with institution and degree present.",
                 "No education section"),
    ATSCriterion("quantified", "Quantified achievements", 15,
                 "Bullets include measurable results (numbers, %, $).",
                 "Experience bullets lack quantified results"),
    ATSCriterion("skills", "Skills section", 15,
                 "A non-empty skills section exists.",
                 "No skills section or it is empty"),
    ATSCriterion("certifications", "Certifications", 5,
                 "Certifications or licenses are present.",
                 "No certifications"),
    ATSCriterion("action_verbs", "Action verbs", 5,
                 "Bullets are led by action verbs.",
                 "Bullets not led by action verbs"),
    ATSCriterion("achievement_focus", "Achievement-focused bullets", 5,
                 "Bullets describe impact, not just duties.",
                 "Bullets read as duties, not achievements"),
    ATSCriterion("length", "Appropriate length", 5,
                 "Resume is concise (max 2 pages).",
                 "Resume appears longer than 2 pages"),
]

MAX_ATS_SCORE: int = sum(c.points for c in ATS_RUBRIC)  # 100

from pipeline.models import ATSReport, CriterionResult

