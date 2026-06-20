from fastapi import APIRouter, File, UploadFile

from app.core.logging import get_logger
from app.schemas.resume import ResumeData
from app.services.resume_processor import ResumeProcessor

router = APIRouter(tags=["resume"])
logger = get_logger(__name__)

_processor = ResumeProcessor()


@router.post("/resume/upload", response_model=ResumeData)
async def upload_resume(file: UploadFile = File(...)) -> ResumeData:
    """Module 1: Upload a resume PDF and get back structured resume data."""
    file_bytes = await file.read()
    logger.info("Received resume upload: %s (%d bytes)", file.filename, len(file_bytes))
    return _processor.parse_pdf(file_bytes)
