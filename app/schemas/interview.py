from enum import Enum

from pydantic import BaseModel, Field, confloat

from app.schemas.job_description import JobDescriptionData
from app.schemas.resume import ResumeData


class ExperienceLevel(str, Enum):
    junior = "junior"
    mid = "mid"
    senior = "senior"


class InterviewQuestionsRequest(BaseModel):
    resume: ResumeData
    job_description: JobDescriptionData
    level: ExperienceLevel = ExperienceLevel.mid


class InterviewQuestionsResponse(BaseModel):
    behavioral: list[str] = Field(default_factory=list)
    technical: list[str] = Field(default_factory=list)
    project_based: list[str] = Field(default_factory=list)


class TranscriptionResponse(BaseModel):
    transcript: str


Score = confloat(ge=0, le=10)


class AnswerEvaluationRequest(BaseModel):
    question: str
    answer: str
    resume: ResumeData
    job_description: JobDescriptionData


class AnswerEvaluationResponse(BaseModel):
    technical: Score
    communication: Score
    relevance: Score
    completeness: Score
    confidence: Score
    overall: Score
    feedback: str
    improvements: list[str] = Field(default_factory=list)


class FinalReportRequest(BaseModel):
    evaluations: list[AnswerEvaluationResponse] = Field(
        ..., min_length=1, description="All per-question evaluations from the interview session"
    )


class FinalReportResponse(BaseModel):
    overall_score: float
    technical_average: float
    communication_average: float
    confidence_average: float
    strong_areas: list[str] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    final_recommendation: str
