from fastapi import APIRouter, File, UploadFile

from app.core.logging import get_logger
from app.schemas.interview import (
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    FinalReportRequest,
    FinalReportResponse,
    InterviewQuestionsRequest,
    InterviewQuestionsResponse,
    TranscriptionResponse,
)
from app.services.qwen_service import QwenService
from app.services.report_aggregator import ReportAggregator
from app.services.whisper_service import WhisperService

router = APIRouter(prefix="/interview", tags=["interview"])
logger = get_logger(__name__)

_qwen = QwenService()
_whisper = WhisperService()
_report_aggregator = ReportAggregator(qwen_service=_qwen)


@router.post("/questions", response_model=InterviewQuestionsResponse)
async def generate_interview_questions(
    payload: InterviewQuestionsRequest,
) -> InterviewQuestionsResponse:
    """Module 7: Interview Question Generator (LLM-backed)."""
    result = await _qwen.generate_questions(
        payload.resume.model_dump(), payload.job_description.model_dump(), payload.level.value
    )
    return InterviewQuestionsResponse(**result)


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_answer(file: UploadFile = File(...)) -> TranscriptionResponse:
    """Module 8: Voice Transcription (Faster Whisper)."""
    file_bytes = await file.read()
    transcript = _whisper.transcribe_audio(file_bytes, file.filename or "audio.wav")
    return TranscriptionResponse(transcript=transcript)


@router.post("/evaluate", response_model=AnswerEvaluationResponse)
async def evaluate_answer(payload: AnswerEvaluationRequest) -> AnswerEvaluationResponse:
    """Module 9: Answer Evaluation (LLM-backed)."""
    result = await _qwen.evaluate_answer(
        payload.question,
        payload.answer,
        payload.resume.model_dump(),
        payload.job_description.model_dump(),
    )
    return AnswerEvaluationResponse(**result)


@router.post("/final-report", response_model=FinalReportResponse)
async def get_final_report(payload: FinalReportRequest) -> FinalReportResponse:
    """Module 10: Final Interview Report (deterministic averages + LLM summary)."""
    return await _report_aggregator.build_final_report(payload.evaluations)
