from pydantic import BaseModel, Field


class ResumeData(BaseModel):
    """Structured representation of a parsed resume.

    `experience`, `education`, `projects`, and `certifications` are kept as
    plain text blocks (one entry per detected item) rather than deeply
    structured sub-objects. The heuristic, non-LLM parser in
    ResumeProcessor cannot reliably split free-text resumes into fields
    like {title, company, start_date, end_date} -- real resumes are too
    inconsistently formatted for regex to do that safely. Keeping the
    raw block per entry is honest about that limitation and is still
    directly usable by the LLM-based analysis/question-generation steps.
    """

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    raw_text: str = ""
