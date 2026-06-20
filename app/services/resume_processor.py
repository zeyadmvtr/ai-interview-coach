"""
Module 1: Resume Processing.

Heuristic (regex/section-based) resume parser. Deliberately does NOT call
the LLM -- this keeps resume upload fast, free, and deterministic. Accuracy
on company/title/date splitting is a known limitation of any non-LLM parser;
see the note on ResumeData. The LLM is reserved for the genuinely
LLM-shaped tasks: feedback, questions, evaluation.
"""
import re

from app.core.exceptions import ResumeParsingError
from app.core.logging import get_logger
from app.schemas.resume import ResumeData
from app.services.pdf_extractor import extract_text_from_pdf
from app.utils.text_cleaning import clean_text, split_bullets

logger = get_logger(__name__)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(\+?\d{1,3}[\s.\-]?)?(\(?\d{2,4}\)?[\s.\-]?){2,4}\d{3,4}"
)

# Section headers we know how to detect, mapped to the ResumeData field they fill.
SECTION_ALIASES: dict[str, list[str]] = {
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
    ],
    "education": ["education", "academic background"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
}

_ALL_HEADER_WORDS = {alias for aliases in SECTION_ALIASES.values() for alias in aliases} | {
    "summary",
    "objective",
    "profile",
    "contact",
    "achievements",
    "publications",
    "languages",
    "interests",
    "references",
}


def _is_section_header(line: str) -> str | None:
    """Return the canonical field name if `line` looks like a section header."""
    candidate = line.strip().strip(":").lower()
    if not candidate or len(candidate.split()) > 4:
        return None

    for field, aliases in SECTION_ALIASES.items():
        if candidate in aliases:
            return field

    if candidate in _ALL_HEADER_WORDS:
        return "_other"  # recognized header but not one we extract into a field

    return None


def _split_into_sections(text: str) -> dict[str, str]:
    """Split resume text into {field_name: raw_block} using header detection."""
    lines = text.split("\n")
    sections: dict[str, list[str]] = {}
    current_field: str | None = None

    for line in lines:
        header_field = _is_section_header(line)
        if header_field is not None:
            current_field = header_field
            sections.setdefault(current_field, [])
            continue
        if current_field:
            sections.setdefault(current_field, []).append(line)

    return {field: "\n".join(content) for field, content in sections.items() if field != "_other"}


def _extract_name(text: str) -> str | None:
    """Best-effort: the candidate's name is usually the first non-empty line
    that isn't an email/phone/header and isn't all-uppercase boilerplate."""
    for line in text.split("\n")[:5]:
        candidate = line.strip()
        if not candidate:
            continue
        if EMAIL_RE.search(candidate) or PHONE_RE.search(candidate):
            continue
        if _is_section_header(candidate):
            continue
        word_count = len(candidate.split())
        if 1 <= word_count <= 5:
            return candidate
    return None


def _extract_skills(block: str) -> list[str]:
    if not block:
        return []
    # Skills sections are usually comma/pipe/bullet separated, not paragraphs.
    normalized = re.sub(r"[\u2022\u25cf\u2023\-\*\u2013\n]", ",", block)
    raw_tokens = re.split(r"[,|/]", normalized)
    seen: set[str] = set()
    skills: list[str] = []
    for token in raw_tokens:
        cleaned = token.strip(" .")
        if not cleaned or len(cleaned) > 40:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            skills.append(cleaned)
    return skills


class ResumeProcessor:
    """Extracts text from a resume PDF and parses it into structured data."""

    def parse_pdf(self, file_bytes: bytes) -> ResumeData:
        raw_text = extract_text_from_pdf(file_bytes)
        return self.parse_text(raw_text)

    def parse_text(self, raw_text: str) -> ResumeData:
        text = clean_text(raw_text)
        if not text:
            raise ResumeParsingError("Resume text is empty after cleaning.")

        sections = _split_into_sections(text)

        email_match = EMAIL_RE.search(text)
        phone_match = PHONE_RE.search(text)

        resume = ResumeData(
            name=_extract_name(text),
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0).strip() if phone_match else None,
            skills=_extract_skills(sections.get("skills", "")),
            experience=split_bullets(sections.get("experience", "")),
            education=split_bullets(sections.get("education", "")),
            projects=split_bullets(sections.get("projects", "")),
            certifications=split_bullets(sections.get("certifications", "")),
            raw_text=text,
        )

        logger.info(
            "Parsed resume: name=%s skills=%d experience_items=%d",
            resume.name,
            len(resume.skills),
            len(resume.experience),
        )
        return resume
