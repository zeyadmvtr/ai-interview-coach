from fastapi import APIRouter

from app.core.logging import get_logger
from app.schemas.job_description import JobDescriptionData, JobDescriptionRequest
from app.services.job_description_processor import JobDescriptionProcessor

router = APIRouter(tags=["job"])
logger = get_logger(__name__)

_processor = JobDescriptionProcessor()


@router.post("/job/analyze", response_model=JobDescriptionData)
async def analyze_job_description(payload: JobDescriptionRequest) -> JobDescriptionData:
    """Module 2: Parse a pasted job description into structured data."""
    return _processor.parse(payload.text)
