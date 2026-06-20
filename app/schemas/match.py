from pydantic import BaseModel, Field

from app.schemas.job_description import JobDescriptionData
from app.schemas.resume import ResumeData


class ResumeMatchRequest(BaseModel):
    resume: ResumeData
    job_description: JobDescriptionData


class ResumeMatchResponse(BaseModel):
    match_score: int
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ResumeFeedbackRequest(BaseModel):
    resume: ResumeData
    job_description: JobDescriptionData


class ResumeFeedbackResponse(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
