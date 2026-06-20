"""
Small, dependency-free text cleaning helpers shared by the resume and
job-description processors.
"""
import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize whitespace/unicode without destroying line structure.

    Section-detection in the resume/JD parsers depends on line breaks, so
    we deliberately do NOT collapse all whitespace into a single line.
    """
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    # Normalize Windows/Mac line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse runs of horizontal whitespace, but keep newlines intact.
    text = re.sub(r"[ \t\xa0]+", " ", text)
    # Collapse 3+ blank lines down to a single blank line.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace on each line.
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def normalize_skill(skill: str) -> str:
    """Normalize a skill token for case-insensitive comparison/dedup."""
    return re.sub(r"[^a-z0-9+#.]", "", skill.lower())


def split_bullets(block: str) -> list[str]:
    """Split a section's text block into individual bullet/entry strings."""
    bullet_markers = re.compile(r"^[\u2022\u25cf\u2023\-\*\u2013]\s*")
    raw_lines = [line for line in block.split("\n") if line.strip()]

    entries: list[str] = []
    current: list[str] = []

    for line in raw_lines:
        is_new_bullet = bool(bullet_markers.match(line))
        cleaned = bullet_markers.sub("", line).strip()

        if is_new_bullet or not current:
            if current:
                entries.append(" ".join(current).strip())
            current = [cleaned]
        else:
            # Continuation of the previous bullet (wrapped line).
            current.append(cleaned)

    if current:
        entries.append(" ".join(current).strip())

    return [e for e in entries if e]
