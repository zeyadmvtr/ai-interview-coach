# AI Interview Coach -- AI Engine

A FastAPI backend that powers an AI Interview Coach: resume parsing, ATS
scoring, resume-to-job matching, AI resume feedback, interview question
generation, voice transcription, answer evaluation, and a final interview
report.

This is an MVP: it is deliberately not over-engineered. There's no
database, no auth, no job queue -- every endpoint is a stateless
request/response. The client (web/mobile app) is responsible for holding
state across the flow (resume -> JD -> ATS -> match -> feedback ->
questions -> per-question transcribe/evaluate -> final report).

## Architecture

```
app/
  api/routes/     FastAPI routers, one file per feature area. Thin: parse
                   request -> call a service -> return the response model.
  core/            Config (pydantic-settings), logging, custom exceptions
                   + FastAPI exception handlers.
  models/          Placeholder for a future persistence layer (none yet --
                   see the docstring in app/models/__init__.py).
  schemas/         Pydantic models: the single source of truth for every
                   request/response shape in the app.
  services/        All business logic lives here. Each module maps to one
                   spec module (resume_processor, job_description_processor,
                   ats_scoring, resume_match, qwen_service, whisper_service,
                   report_aggregator) plus a small pdf_extractor helper.
  prompts/         Every LLM prompt as plain Python string-builders. Never
                   imported by anything except qwen_service.py.
  utils/           Small, dependency-free helpers (text cleaning, safe JSON
                   parsing of LLM output).
tests/             Pytest unit + API tests. Everything that doesn't need a
                   live Ollama/Whisper model is tested (resume/JD parsing,
                   ATS scoring, matching, JSON parsing, route wiring).
```

### Why some modules use the LLM and some don't

- **Resume parsing, JD parsing, ATS scoring, resume matching** are
  rule-based (regex/heuristics), not LLM calls. They need to be fast,
  free, deterministic, and explainable -- an ATS score that changes
  between two runs on the same input would be a bad product experience.
- **Resume feedback, question generation, answer evaluation, and the
  qualitative part of the final report** genuinely need judgment and
  natural language generation, so they go through `QwenService`, the one
  centralized client for Ollama's `qwen3:8b`. Every prompt it uses is
  defined in `app/prompts/` -- nothing is hardcoded inline in the service.
  Ollama's JSON mode (`format: "json"`) plus a defensive parser
  (`utils/json_parser.py`) guarantee the service never returns raw,
  unparseable text to the API layer.
- The **final interview report's numeric averages** are computed in plain
  Python (`report_aggregator.py`), not by the LLM -- only the narrative
  (`strong_areas`, `weak_areas`, `final_recommendation`) is LLM-generated,
  grounded in the already-computed numbers.

### Known MVP limitation

The heuristic resume/JD parsers extract `experience`, `education`,
`projects`, and `certifications` as raw text blocks (one string per
detected bullet/entry) rather than fully structured objects with separate
`title`/`company`/`dates` fields. Real-world resumes are too
inconsistently formatted for regex to split that reliably without an LLM.
A natural next step beyond this MVP is an LLM-assisted resume parser for
higher-fidelity structured extraction.

## Prerequisites

- Python 3.12
- [Ollama](https://ollama.com) installed locally, with the model pulled:
  ```bash
  ollama pull qwen3:8b
  ```
- `ffmpeg` installed (required by faster-whisper to decode mp3/m4a audio).
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`

## Local Setup

```bash
# 1. Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# edit .env if your Ollama host/port or whisper settings differ

# 4. Start Ollama and the model (separate terminal)
ollama serve
ollama run qwen3:8b

# 5. Run the API
uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`, with interactive docs
at `http://localhost:8000/docs`.

First request to `/interview/transcribe` will be slow (faster-whisper
downloads/loads the model weights on first use, then keeps it in memory
for subsequent requests).

## Running Tests

```bash
pytest
```

All tests run without a live Ollama or Whisper model -- they cover the
deterministic parsing/scoring/matching logic and route wiring, and mock
nothing else by design (the LLM-backed endpoints are integration-tested
manually against a real Ollama instance, since mocking the model would
just test the mock).

## Docker

```bash
docker build -t ai-interview-coach .
docker run -p 8000:8000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  ai-interview-coach
```

Ollama is **not** bundled in this image -- run `ollama serve` on the host
(or as a sibling container) and point `OLLAMA_HOST` at it.

## API Endpoints

| Method | Path                      | Module | Description                                  |
|--------|---------------------------|--------|-----------------------------------------------|
| POST   | `/resume/upload`          | 1      | Upload resume PDF -> structured resume data   |
| POST   | `/job/analyze`            | 2      | Paste JD text -> structured JD data           |
| POST   | `/ats-score`               | 3      | Resume + JD -> ATS compatibility score        |
| POST   | `/resume-match`           | 4      | Resume + JD -> match score, gaps              |
| POST   | `/resume-feedback`        | 6      | Resume + JD -> AI strengths/weaknesses/recs   |
| POST   | `/interview/questions`    | 7      | Resume + JD + level -> interview questions    |
| POST   | `/interview/transcribe`   | 8      | Audio file -> transcript                      |
| POST   | `/interview/evaluate`     | 9      | Question + answer -> per-dimension scores     |
| POST   | `/interview/final-report` | 10     | All evaluations -> aggregated final report    |

See `/docs` for full request/response schemas (auto-generated from the
Pydantic models in `app/schemas/`).

## Example End-to-End Flow

```bash
# 1. Upload resume
curl -X POST http://localhost:8000/resume/upload \
  -F "file=@resume.pdf"

# 2. Analyze job description
curl -X POST http://localhost:8000/job/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Senior Backend Engineer... (full JD text)"}'

# 3. Get ATS score (pass the JSON output of steps 1 and 2)
curl -X POST http://localhost:8000/ats-score \
  -H "Content-Type: application/json" \
  -d '{"resume": {...}, "job_description": {...}}'

# 4-10: same pattern -- each endpoint is independent and stateless;
# the client threads the data between calls.
```

## Future Improvements (post-MVP)

- LLM-assisted resume/JD parsing for higher-fidelity structured extraction
- Persistence layer (sessions, resume/JD history, report storage)
- Auth + multi-user support
- Streaming responses for question generation / evaluation
- Background job queue for transcription on long audio files
- Caching of Ollama responses for identical resume+JD pairs
