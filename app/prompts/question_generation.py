"""Prompt for Module 7: Interview Question Generator (QwenService.generate_questions)."""
import json

SYSTEM_PROMPT = (
    "You are an experienced technical interviewer and hiring manager. You write "
    "sharp, role-specific interview questions tailored to a candidate's actual "
    "background and the target job. You ALWAYS respond with a single valid JSON "
    "object and nothing else -- no markdown fences, no preamble."
)

_OUTPUT_SCHEMA = {
    "behavioral": ["string"],
    "technical": ["string"],
    "project_based": ["string"],
}

_LEVEL_GUIDANCE = {
    "junior": (
        "The candidate is JUNIOR level (0-2 years). Favor fundamentals, "
        "willingness to learn, and guided problem-solving over deep system design."
    ),
    "mid": (
        "The candidate is MID level (2-5 years). Favor practical trade-offs, "
        "ownership of features end-to-end, and moderate system design depth."
    ),
    "senior": (
        "The candidate is SENIOR level (5+ years). Favor system design, "
        "technical leadership, mentoring, ambiguous trade-offs, and scale."
    ),
}


def build_prompt(resume: dict, job_description: dict, level: str) -> str:
    level_note = _LEVEL_GUIDANCE.get(level, _LEVEL_GUIDANCE["mid"])

    return f"""Generate interview questions for this candidate and role.

RESUME (structured):
{json.dumps(resume, indent=2)}

JOB DESCRIPTION (structured):
{json.dumps(job_description, indent=2)}

CANDIDATE LEVEL: {level}
{level_note}

Generate:
- behavioral: 4 behavioral/soft-skill questions (use STAR-friendly phrasing)
- technical: 5 technical questions drawn from the required/preferred skills in the job description
- project_based: 3 questions that reference SPECIFIC projects or experience listed in the resume

Questions must be specific, not generic filler. Reference real skills, technologies,
or project names found in the resume/job description wherever possible.

Respond with ONLY a JSON object matching exactly this shape (no extra keys):
{json.dumps(_OUTPUT_SCHEMA, indent=2)}
"""
