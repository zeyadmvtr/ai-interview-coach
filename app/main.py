"""
AI Interview Coach -- FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Prerequisites running alongside this app:
    ollama serve              # in one terminal
    ollama run qwen3:8b       # pulls/starts the model
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ats, interview, job, match, resume
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Interview Coach API starting up (env=%s)", settings.app_env)
    logger.info("Ollama target: %s using model %s", settings.ollama_host, settings.ollama_model)
    yield
    logger.info("AI Interview Coach API shutting down")


app = FastAPI(
    title="AI Interview Coach API",
    description="AI engine for resume analysis, ATS scoring, and mock interview coaching.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP: open CORS. Restrict to known origins before production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(resume.router)
app.include_router(job.router)
app.include_router(ats.router)
app.include_router(match.router)
app.include_router(interview.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {
        "status": "ok",
        "environment": settings.app_env,
        "ollama_model": settings.ollama_model,
    }
