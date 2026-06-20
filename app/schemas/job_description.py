from pydantic import BaseModel, Field


class JobDescriptionRequest(BaseModel):
    text: str = Field(..., min_length=20, description="Raw job description text")


class JobDescriptionData(BaseModel):
    role_title: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_requirements: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    raw_text: str = ""
