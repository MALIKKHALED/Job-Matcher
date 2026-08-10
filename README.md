# Agentic Job Matcher

An agentic AI pipeline that turns any job posting + your resume into a complete, ready-to-send application package:

**Scrape → Extract → ATS Score → Enhance → Match → Cover Letter**

Paste a job URL and your resume once, and the pipeline analyzes the posting, scores your resume against a fixed ATS rubric, produces an optimized, fact-traceable resume, evaluates how well you actually fit the role, and writes a personalized cover letter — all with a **no-invention guarantee**.

---

## How it works

Six CrewAI agents run sequentially. Each writes its structured output to `ai_agent_output/` so you can audit every stage.

| # | Stage | Agent | Input | Output |
|---|-------|-------|-------|--------|
| 1 | **Scrape** | Scraper | job URL | `JobDetails` — company, title, description, responsibilities, requirements, required skills |
| 2 | **Extract** | Resume Extractor | raw resume text | `ResumeProfile` — structured contact, summary, skills, experience, education, certifications |
| 3 | **ATS Score** | ATS Compliance Judge | `ResumeProfile` + fixed rubric | `ATSReport` — score out of 100, per-criterion breakdown, deductions, critical missing |
| 4 | **Enhance** | Resume Enhancer | job details + profile + ATS report (+ optional extra info) | `OptimizedResume` — repackaged Markdown, `changes` audit, `missing_info_report` |
| 5 | **Match** | Job Match Evaluator | job details + optimized resume | `MatchReport` — match %, matched/missing skills, strengths, gaps, recommendation |
| 6 | **Cover Letter** | Cover Letter Writer | job details + optimized resume + match report | `CoverLetter` — subject line, Markdown body, "verify before sending" notes |

### Key design decisions

- **Static ATS rubric.** The scoring criteria and weights live in `pipeline/ats_rubric.py` (sum = 100). The LLM judge applies them exactly; the rubric is never decided by the model.
- **Deterministic recommendation.** The match agent suggests a verdict, but the final recommendation is always recomputed in code from `match_percentage`:

  | Match % | Recommendation |
  |---------|----------------|
  | ≥ 70 | Apply now |
  | 45 – 69 | Improve then apply |
  | < 45 | Do not apply |

- **No-invention guarantee.** The enhancer may only rephrase, reorder, and align *existing facts* from your resume. It can never add a skill, metric, company, degree, or date that is not in your resume. Everything it cannot safely add goes into `missing_info_report` as a conditional suggestion (e.g. "If you have X, add it to skills").
- **Transparent changes.** Every edit is logged in the `changes` list, and the UI renders it as a **"Changes Applied (no-invention audit)"** card so you can verify nothing was fabricated.
- **Iterate safely.** Use the optional *Extra info* field to feed trusted facts (certifications, location, LinkedIn, corrected dates) into the enhancer — re-run as many times as you like. ATS scores the *base* resume, so to raise the ATS score you must improve the resume text itself.

---

## Project structure

```
Job-Matcher/
├── app/
│   ├── main.py              # FastAPI app: pipeline API + static file server
│   ├── core/config.py       # Settings, LLM + ScrapeGraphAI client factories
│   └── static/              # Web UI (index.html, styles.css, app.js)
├── pipeline/
│   ├── agents.py            # 6 CrewAI agent definitions
│   ├── tasks.py             # 6 task definitions + prompt rules
│   ├── crew.py              # build_tasks / build_pipeline / build_crew
│   ├── models.py            # Pydantic schemas for every structured output
│   ├── ats_rubric.py        # Static ATS rubric (single source of truth)
│   └── tools.py             # ScrapeJobPage tool (ScrapeGraphAI)
├── services/
│   └── pipeline.py          # Orchestration: run_pipeline(), PipelineResult,
│                            #   compute_recommendation()
├── tests/                   # Agent smoke tests + API/pipeline e2e (gitignored)
├── ai_agent_output/         # step_1..step_6 per-stage artifacts (gitignored)
├── .env.example
└── pyproject.toml
```

---

## Prerequisites

- **Python 3.12+**
- An **OpenRouter API key** — `https://openrouter.ai/keys`
- A **ScrapeGraphAI** API key (cloud scraper) — `https://scrapegraph.ai`

---

## Quickstart

```bash
# 1. Clone and install
git clone <your-repo-url>
cd Job-Matcher
pip install -e .

# 2. Configure secrets
copy .env.example .env        # then fill in your keys
# OPENROUTER_API_KEY=sk-or-...
# SGAI_API_KEY=...

# 3. Run the API + UI
python -m uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** in your browser.

### Using the web UI

1. Paste a job posting URL (LinkedIn, etc.) and your resume text.
2. *(Optional)* Add extra info to incorporate — certifications, location, LinkedIn URL, corrected dates.
3. Click **Run Pipeline** and wait (~30–60 s, 6 LLM calls).
4. Review the ATS score, match %, recommendation, missing-info checklist, changes audit, optimized resume, and cover letter. Download the `.md` files when ready.

---

## API reference

### `POST /api/pipeline`

Start a pipeline run. Runs in the background; returns immediately.

```bash
curl -X POST http://127.0.0.1:8000/api/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "job_url": "https://www.linkedin.com/jobs/view/123456",
    "resume_text": "John Carter\nEmail: ...\n...",
    "user_supplied_info": "Location: Cairo. AWS Certified Solutions Architect."
  }'
```

Response (`202 Accepted`):

```json
{ "job_id": "a1b2c3d4e5f6...", "status": "running" }
```

### `GET /api/pipeline/{job_id}`

Poll the job until it finishes.

```json
{ "status": "running" }
{ "status": "error", "error": "..." }
{ "status": "done", "result": { "job_details": {...}, "resume_profile": {...},
  "ats_report": {...}, "optimized_resume": {...}, "match_report": {...},
  "cover_letter": {...} } }
```

### Quick script

```python
import json, time, urllib.request

BASE = "http://127.0.0.1:8000"

def run(job_url: str, resume_text: str, extra: str = "") -> dict:
    req = urllib.request.Request(
        f"{BASE}/api/pipeline",
        data=json.dumps({"job_url": job_url, "resume_text": resume_text,
                         "user_supplied_info": extra}).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    job_id = json.load(urllib.request.urlopen(req))["job_id"]
    while True:
        time.sleep(3)
        res = json.load(urllib.request.urlopen(f"{BASE}/api/pipeline/{job_id}"))
        if res["status"] == "running":
            continue
        return res
```

---

## ATS rubric (100 points)

Defined once in `pipeline/ats_rubric.py` — edit there to change scoring.

| Criterion | Points |
|-----------|:------:|
| Contact — email | 4 |
| Contact — phone | 4 |
| Contact — location | 2 |
| Professional summary | 10 |
| Experience section (company, title, dates) | 15 |
| Education (institution, degree) | 15 |
| Quantified achievements (numbers / % / $) | 15 |
| Skills section (non-empty) | 15 |
| Certifications | 5 |
| Action verbs | 5 |
| Achievement-focused bullets | 5 |
| Appropriate length (≤ 2 pages) | 5 |
| **Total** | **100** |

---

## Configuration (`.env`)

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | — | OpenRouter API key used for all agents |
| `OPENROUTER_MODEL` | No | `openrouter/auto-beta` | Any bare model slug, e.g. `anthropic/claude-sonnet-4-20250514` |
| `LLM_TEMPERATURE` | No | `0` | Sampling temperature (0 = deterministic) |
| `SGAI_API_KEY` | Yes | — | ScrapeGraphAI cloud key for the job scraper |

To swap the LLM provider or scraper, extend `build_llm()` / `build_scrapegraph_client()` in `app/core/config.py`.

---

## Testing

`tests/` contains per-agent smoke tests plus end-to-end API and pipeline tests (gitignored so credentials/CVs stay local):

```bash
python tests/test_api.py          # API round-trip: POST → poll → done
python tests/test_full_pipeline.py
```

The project was validated end-to-end on the UI with 5 CVs ranging from weak to excellent: honest "Do not apply" verdicts for unfit candidates, and the full *fix → re-run → improve* loop for candidates who should enhance before applying.

---

## Output artifacts

Each stage also writes a JSON file to `ai_agent_output/` for auditing:

```
step_1_scraped_results.json
step_2_resume_profile.json
step_3_ats_report.json
step_4_optimized_resume.json
step_5_match_report.json
step_6_cover_letter.json
```

---

## Disclaimer

The ATS score, match percentage, and recommendation are AI-generated guidance for job seekers to help prioritize applications — **not** a guarantee of results. Always verify generated facts before sending an application.

## License

[MIT](LICENSE) © 2026 Malik khalid El-Lethy
