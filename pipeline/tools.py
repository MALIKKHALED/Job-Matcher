"""Custom tools for the crew agents."""

import json

from crewai.tools import tool

from app.core.config import build_scrapegraph_client
from pipeline.models import JobDetails

@tool("ScrapeJobPage")
def scrape_job_page(url: str) -> str:
    """
    Scrape a job posting URL and return the full page content as Markdown text.
    
    Example:
        url = "https://www.amazon.eg/-/en/dp/B0B1ZY1Z5G"
    """

    client = build_scrapegraph_client()
    result = client.extract(
            url=url,
            prompt=(
            "Extract the job posting details: company name, company about, "
            "job title, job description, key responsibilities, requirements "
            "with required skills and qualifications, company culture, and anu additional improtant notes or information."
            ),
            schema=JobDetails.model_json_schema(),
        )

    if result.status == "error":
        return f"ERROR: {result.error}"

    if result.data is None:
        return str(result)

    payload = result.data.model_dump()
    data = payload.get("json_data") or payload
    if isinstance(data, dict):
        data.setdefault("page_url", url)
    return json.dumps(data, ensure_ascii=False)