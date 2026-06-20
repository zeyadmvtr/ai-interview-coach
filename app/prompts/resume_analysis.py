"""Prompt for Module 6: AI Resume Analysis (QwenService.analyze_resume)."""
import json

SYSTEM_PROMPT = (
    "You are a senior technical recruiter and resume coach with 15 years of "
    "experience hiring for software and data roles. You give honest, specific, "
    "actionable feedback. You ALWAYS respond with a single valid JSON object "
    "and nothing else -- no markdown fences, no preamble, no explanation "
    "outside the JSON."
)

_OUTPUT_SCHEMA = {
    "strengths": ["string"],
    "weaknesses": ["string"],
    "missing_skills": ["string"],
    "recommendations": ["string"],
}


def build_prompt(resume: dict, job_description: dict) -> str:
    return f"""Analyze this candidate's resume against the target job description.

RESUME (structured):
{json.dumps(resume, indent=2)}

JOB DESCRIPTION (structured):
{json.dumps(job_description, indent=2)}

Evaluate the fit and produce:
- strengths: 3-6 specific strengths this resume demonstrates for THIS role
- weaknesses: 3-6 specific gaps or weak points relative to THIS role
- missing_skills: required/preferred skills from the job description that are absent from the resume
- recommendations: 3-6 concrete, actionable edits the candidate should make to their resume

Respond with ONLY a JSON object matching exactly this shape (no extra keys):
{json.dumps(_OUTPUT_SCHEMA, indent=2)}
"""
