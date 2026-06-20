"""
Module 3: ATS Compatibility Score.

Deterministic, rule-based scoring -- no LLM involved. ATS scores need to be
explainable and reproducible, which rules out a model in the loop.

Score components (sum to 100):
    Keyword Match   = 40 points
    Resume Structure = 20 points
    Readability      = 20 points
    Impact Score     = 20 points
"""
import re

from app.core.logging import get_logger
from app.schemas.job_description import JobDescriptionData
from app.schemas.resume import ResumeData
from app.utils.text_cleaning import normalize_skill

logger = get_logger(__name__)

IMPACT_PATTERNS = [
    re.compile(r"\d+(\.\d+)?\s*%"),  # percentages: "30%"
    re.compile(r"\$\s?\d[\d,]*"),  # money: "$50,000"
    re.compile(r"\b\d[\d,]*\+?\b"),  # bare numbers: "10,000", "5+"
]

# A crude but effective heuristic: lines with these markers usually indicate
# heavy graphics/columns/icons that ATS parsers choke on. We can't inspect
# the original PDF layout here (we only see extracted text), so we look for
# proxy signals in the extracted text itself.
GLYPH_NOISE_RE = re.compile(r"[\uf000-\uf8ff\u2190-\u21ff\u25a0-\u25ff]")


class ATSScoringEngine:
    """Computes a 0-100 ATS compatibility score with a transparent breakdown."""

    def score(self, resume: ResumeData, job_description: JobDescriptionData) -> tuple[int, dict]:
        keyword_score, keyword_detail = self._score_keyword_match(resume, job_description)
        structure_score, structure_detail = self._score_structure(resume)
        readability_score, readability_detail = self._score_readability(resume)
        impact_score, impact_detail = self._score_impact(resume)

        total = round(keyword_score + structure_score + readability_score + impact_score)
        total = max(0, min(100, total))

        breakdown = {
            "keyword_match": {"score": keyword_score, "max": 40, **keyword_detail},
            "structure": {"score": structure_score, "max": 20, **structure_detail},
            "readability": {"score": readability_score, "max": 20, **readability_detail},
            "impact": {"score": impact_score, "max": 20, **impact_detail},
        }

        logger.info("ATS score=%d for resume=%s", total, resume.name)
        return total, breakdown

    @staticmethod
    def _score_keyword_match(
        resume: ResumeData, job_description: JobDescriptionData
    ) -> tuple[float, dict]:
        jd_skills = job_description.required_skills + job_description.preferred_skills
        if not jd_skills:
            # No JD skills to compare against: be neutral rather than punitive.
            return 40.0, {"matched": [], "total_jd_skills": 0, "note": "No JD skills detected"}

        resume_skill_keys = {normalize_skill(s) for s in resume.skills}
        # Also search the full resume text, since skills are sometimes only
        # mentioned inside experience/project bullets, not a skills section.
        resume_text_key = normalize_skill(resume.raw_text)

        matched = []
        for skill in jd_skills:
            key = normalize_skill(skill)
            if not key:
                continue
            if key in resume_skill_keys or key in resume_text_key:
                matched.append(skill)

        ratio = len(matched) / len(jd_skills)
        score = round(ratio * 40, 1)
        return score, {"matched": matched, "total_jd_skills": len(jd_skills)}

    @staticmethod
    def _score_structure(resume: ResumeData) -> tuple[float, dict]:
        present = {
            "summary": bool(re.search(r"\bsummary\b|\bobjective\b|\bprofile\b", resume.raw_text, re.I)),
            "skills": bool(resume.skills),
            "experience": bool(resume.experience),
            "projects": bool(resume.projects),
            "education": bool(resume.education),
        }
        score = round((sum(present.values()) / len(present)) * 20, 1)
        return score, {"sections_present": present}

    @staticmethod
    def _score_readability(resume: ResumeData) -> tuple[float, dict]:
        text = resume.raw_text
        deductions = 0.0
        reasons = []

        if not text.strip():
            return 0.0, {"reasons": ["Empty resume text"]}

        noise_matches = len(GLYPH_NOISE_RE.findall(text))
        if noise_matches > 5:
            deductions += 6
            reasons.append("Heavy use of special glyphs/icons detected (may indicate image-based formatting)")

        avg_line_len = sum(len(line) for line in text.split("\n")) / max(text.count("\n") + 1, 1)
        if avg_line_len < 8:
            deductions += 6
            reasons.append("Very short average line length -- possible multi-column/image-heavy layout")

        word_count = len(text.split())
        if word_count < 150:
            deductions += 5
            reasons.append("Resume content is very short, ATS parsers may extract little usable text")
        elif word_count > 1200:
            deductions += 3
            reasons.append("Resume is unusually long, consider tightening to 1-2 pages")

        if not re.search(r"[a-zA-Z]{3,}", text):
            deductions += 5
            reasons.append("Little to no readable alphabetic text extracted")

        score = max(0.0, round(20 - deductions, 1))
        return score, {"reasons": reasons or ["No readability issues detected"]}

    @staticmethod
    def _score_impact(resume: ResumeData) -> tuple[float, dict]:
        entries = resume.experience + resume.projects
        if not entries:
            return 0.0, {"quantified_entries": 0, "total_entries": 0}

        quantified = 0
        for entry in entries:
            if any(pattern.search(entry) for pattern in IMPACT_PATTERNS):
                quantified += 1

        ratio = quantified / len(entries)
        score = round(ratio * 20, 1)
        return score, {"quantified_entries": quantified, "total_entries": len(entries)}
