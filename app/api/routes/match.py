from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.match import (
    ResumeFeedbackRequest,
    ResumeFeedbackResponse,
    ResumeMatchRequest,
    ResumeMatchResponse,
)
from app.services.qwen_service import QwenService
from app.services.resume_match import ResumeMatchEngine

router = APIRouter(tags=["match"])
logger = get_logger(__name__)

_match_engine = ResumeMatchEngine()
_qwen = QwenService()


@router.post("/resume-match", response_model=ResumeMatchResponse)
async def get_resume_match(payload: ResumeMatchRequest) -> ResumeMatchResponse:
    """Module 4: Resume Match Engine (rule-based, no LLM)."""
    result = _match_engine.match(payload.resume, payload.job_description)
    return ResumeMatchResponse(**result)


@router.post("/resume-feedback", response_model=ResumeFeedbackResponse)
async def get_resume_feedback(payload: ResumeFeedbackRequest) -> ResumeFeedbackResponse:
    """Module 6: AI Resume Analysis (LLM-backed)."""
    result = await _qwen.analyze_resume(
        payload.resume.model_dump(), payload.job_description.model_dump()
    )
    return ResumeFeedbackResponse(**result)
