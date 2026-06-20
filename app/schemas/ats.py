from typing import Any

from pydantic import BaseModel

from app.schemas.job_description import JobDescriptionData
from app.schemas.resume import ResumeData


class ATSScoreRequest(BaseModel):
    resume: ResumeData
    job_description: JobDescriptionData


class ATSScoreResponse(BaseModel):
    ats_score: int
    breakdown: dict[str, Any]
