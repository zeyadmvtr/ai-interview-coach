"""
Module 2: Job Description Processing.

Same heuristic, non-LLM approach as ResumeProcessor, for the same reasons:
fast, deterministic, no model dependency for a structural-parsing task.
"""
import re

from app.core.exceptions import JobDescriptionParsingError
from app.core.logging import get_logger
from app.schemas.job_description import JobDescriptionData
from app.utils.text_cleaning import clean_text, split_bullets

logger = get_logger(__name__)

EXPERIENCE_RE = re.compile(
    r"(\d+\+?\s*(?:-\s*\d+\s*)?years?(?:\s+of)?\s+(?:relevant\s+)?experience)",
    re.IGNORECASE,
)

SECTION_ALIASES: dict[str, list[str]] = {
    "required_skills": [
        "required skills",
        "requirements",
        "required qualifications",
        "must have",
        "minimum qualifications",
    ],
    "preferred_skills": [
        "preferred skills",
        "preferred qualifications",
        "nice to have",
        "bonus points",
        "good to have",
    ],
    "responsibilities": [
        "responsibilities",
        "key responsibilities",
        "what you'll do",
        "duties",
        "role overview",
    ],
}

_ALL_HEADER_WORDS = {alias for aliases in SECTION_ALIASES.values() for alias in aliases} | {
    "about us",
    "about the role",
    "benefits",
    "perks",
    "compensation",
    "how to apply",
    "company overview",
}


def _is_section_header(line: str) -> str | None:
    candidate = line.strip().strip(":").lower()
    if not candidate or len(candidate.split()) > 6:
        return None

    for field, aliases in SECTION_ALIASES.items():
        if candidate in aliases:
            return field

    if candidate in _ALL_HEADER_WORDS:
        return "_other"

    return None


def _split_into_sections(text: str) -> dict[str, str]:
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


def _extract_skills_from_block(block: str) -> list[str]:
    if not block:
        return []
    items = split_bullets(block)
    if len(items) <= 1 and block.count(",") > 1:
        # Single paragraph, comma separated rather than bulleted.
        items = [t.strip() for t in block.split(",")]
    cleaned = []
    seen: set[str] = set()
    for item in items:
        item = item.strip(" .")
        if not item or len(item) > 80:
            continue
        key = item.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(item)
    return cleaned


def _extract_role_title(text: str) -> str | None:
    for line in text.split("\n")[:5]:
        candidate = line.strip()
        if candidate and not _is_section_header(candidate) and len(candidate.split()) <= 8:
            return candidate
    return None


class JobDescriptionProcessor:
    """Parses raw job description text into structured data."""

    def parse(self, raw_text: str) -> JobDescriptionData:
        text = clean_text(raw_text)
        if not text:
            raise JobDescriptionParsingError("Job description text is empty after cleaning.")

        sections = _split_into_sections(text)
        experience_match = EXPERIENCE_RE.search(text)

        jd = JobDescriptionData(
            role_title=_extract_role_title(text),
            required_skills=_extract_skills_from_block(sections.get("required_skills", "")),
            preferred_skills=_extract_skills_from_block(sections.get("preferred_skills", "")),
            experience_requirements=experience_match.group(0) if experience_match else None,
            responsibilities=split_bullets(sections.get("responsibilities", "")),
            raw_text=text,
        )

        logger.info(
            "Parsed JD: role=%s required_skills=%d preferred_skills=%d",
            jd.role_title,
            len(jd.required_skills),
            len(jd.preferred_skills),
        )
        return jd
