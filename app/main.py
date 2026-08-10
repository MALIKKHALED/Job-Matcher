"""FastAPI application: pipeline API + static UI."""

import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from services.pipeline import PipelineResult, run_pipeline

app = FastAPI(title="Agentic Job Matcher")


class PipelineRequest(BaseModel):
    job_url: str = Field(min_length=1)
    resume_text: str = Field(min_length=1)
    user_supplied_info: str = ""


@dataclass
class Job:
    status: str = "running"  # running | done | error
    result: PipelineResult | None = None
    error: str | None = None


JOBS: dict[str, Job] = {}


def _run(job_id: str, job_url: str, resume_text: str, user_supplied_info: str) -> None:
    try:
        result = run_pipeline(job_url, resume_text, user_supplied_info)
        JOBS[job_id].status = "done"
        JOBS[job_id].result = result
    except Exception as exc:  # surface error to the client
        JOBS[job_id].status = "error"
        JOBS[job_id].error = str(exc)


@app.post("/api/pipeline", status_code=202)
async def start_pipeline(req: PipelineRequest, background: BackgroundTasks) -> dict:
    job_id = uuid.uuid4().hex
    JOBS[job_id] = Job(status="running")
    background.add_task(_run, job_id, req.job_url, req.resume_text, req.user_supplied_info)
    return {"job_id": job_id, "status": "running"}


@app.get("/api/pipeline/{job_id}")
async def get_pipeline(job_id: str) -> dict[str, Any]:
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == "running":
        return {"status": "running"}
    if job.status == "error":
        return {"status": "error", "error": job.error}
    return {"status": "done", "result": job.result.model_dump()}


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")