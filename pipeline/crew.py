"""Assemble the full agentic pipeline crew."""

from crewai import Crew, Process

from pipeline.agents import (
    ats_scorer_agent,
    cover_letter_writer_agent,
    match_evaluator_agent,
    resume_enhancer_agent,
    resume_extractor_agent,
    scraper_agent,
)
from pipeline.tasks import (
    ats_score_task,
    cover_letter_task,
    enhance_resume_task,
    extract_resume_task,
    match_eval_task,
    scrape_job_task,
)


def build_crew() -> Crew:
    scrape_task = scrape_job_task()
    resume_task = extract_resume_task()
    ats_task = ats_score_task(context=[resume_task])
    enhance_task = enhance_resume_task(context=[scrape_task, resume_task, ats_task])
    match_task = match_eval_task(context=[scrape_task, enhance_task])
    cover_task = cover_letter_task(context=[scrape_task, enhance_task, match_task])

    return Crew(
        agents=[
            scraper_agent(),
            resume_extractor_agent(),
            ats_scorer_agent(),
            resume_enhancer_agent(),
            match_evaluator_agent(),
            cover_letter_writer_agent(),
        ],
        tasks=[scrape_task, resume_task, ats_task, enhance_task, match_task, cover_task],
        process=Process.sequential,
        verbose=False,
        memory=False,
    )