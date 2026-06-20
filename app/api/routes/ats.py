from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.ats import ATSScoreRequest, ATSScoreResponse
from app.services.ats_scoring import ATSScoringEngine

router = APIRouter(tags=["ats"])
logger = get_logger(__name__)

_engine = ATSScoringEngine()


@router.post("/ats-score", response_model=ATSScoreResponse)
async def get_ats_score(payload: ATSScoreRequest) -> ATSScoreResponse:
    """Module 3: ATS Compatibility Score."""
    score, breakdown = _engine.score(payload.resume, payload.job_description)
    return ATSScoreResponse(ats_score=score, breakdown=breakdown)
