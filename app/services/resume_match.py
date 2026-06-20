"""
Module 4: Resume Match Engine.

Rule-based skill overlap scoring. Required skills are weighted more heavily
than preferred skills since missing a "required" skill matters more.
"""
from app.core.logging import get_logger
from app.schemas.job_description import JobDescriptionData
from app.schemas.resume import ResumeData
from app.utils.text_cleaning import normalize_skill

logger = get_logger(__name__)

REQUIRED_WEIGHT = 0.7
PREFERRED_WEIGHT = 0.3


class ResumeMatchEngine:
    """Computes an overall match score between a resume and a job description."""

    def match(self, resume: ResumeData, job_description: JobDescriptionData) -> dict:
        resume_keys = {normalize_skill(s): s for s in resume.skills if normalize_skill(s)}
        resume_text_key = normalize_skill(resume.raw_text)

        def is_present(skill: str) -> bool:
            key = normalize_skill(skill)
            return bool(key) and (key in resume_keys or key in resume_text_key)

        required = job_description.required_skills
        preferred = job_description.preferred_skills

        matched_skills: list[str] = []
        missing_skills: list[str] = []

        for skill in required + preferred:
            (matched_skills if is_present(skill) else missing_skills).append(skill)

        required_ratio = (
            sum(1 for s in required if is_present(s)) / len(required) if required else 1.0
        )
        preferred_ratio = (
            sum(1 for s in preferred if is_present(s)) / len(preferred) if preferred else 1.0
        )

        if not required and not preferred:
            match_score = 50  # No JD skill data to compare against -- neutral, not zero.
        else:
            match_score = round((required_ratio * REQUIRED_WEIGHT + preferred_ratio * PREFERRED_WEIGHT) * 100)

        recommendations = self._build_recommendations(missing_skills, required)

        result = {
            "match_score": max(0, min(100, match_score)),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "recommendations": recommendations,
        }

        logger.info("Resume match score=%d (matched=%d, missing=%d)", result["match_score"], len(matched_skills), len(missing_skills))
        return result

    @staticmethod
    def _build_recommendations(missing_skills: list[str], required_skills: list[str]) -> list[str]:
        if not missing_skills:
            return ["Resume covers all detected job skills -- no critical gaps found."]

        recommendations = []
        missing_required = [s for s in missing_skills if s in required_skills]

        if missing_required:
            top = ", ".join(missing_required[:5])
            recommendations.append(
                f"Add or highlight experience with these required skills if you have it: {top}."
            )

        missing_preferred = [s for s in missing_skills if s not in required_skills]
        if missing_preferred:
            top = ", ".join(missing_preferred[:5])
            recommendations.append(
                f"Consider mentioning these preferred (nice-to-have) skills if applicable: {top}."
            )

        recommendations.append(
            "If you genuinely lack a skill, consider a quick course or personal project before applying."
        )
        return recommendations
