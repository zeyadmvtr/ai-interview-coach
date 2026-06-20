"""Prompt for Module 9: Answer Evaluation (QwenService.evaluate_answer)."""
import json

SYSTEM_PROMPT = (
    "You are a rigorous but fair technical interviewer scoring a candidate's "
    "spoken interview answer (transcribed from audio, so it may contain minor "
    "transcription artifacts -- do not penalize for that). You ALWAYS respond "
    "with a single valid JSON object and nothing else -- no markdown fences, "
    "no preamble."
)

_OUTPUT_SCHEMA = {
    "technical": "number 0-10",
    "communication": "number 0-10",
    "relevance": "number 0-10",
    "completeness": "number 0-10",
    "confidence": "number 0-10",
    "overall": "number 0-10",
    "feedback": "string, 2-4 sentences",
    "improvements": ["string"],
}


def build_prompt(question: str, answer: str, resume: dict, job_description: dict) -> str:
    return f"""Evaluate this interview answer.

QUESTION:
{question}

CANDIDATE'S ANSWER (transcribed from speech):
{answer}

CANDIDATE'S RESUME (for context on claimed experience):
{json.dumps(resume, indent=2)}

JOB DESCRIPTION (for context on what "good" looks like for this role):
{json.dumps(job_description, indent=2)}

Score the answer 0-10 on each dimension:
- technical: correctness and depth of technical content (use 5 as a neutral baseline for purely behavioral questions with no technical content)
- communication: clarity, structure, conciseness
- relevance: how directly the answer addresses the question asked
- completeness: whether the answer covers what a strong answer would cover
- confidence: how confident and decisive the candidate sounds in their wording (not arrogance)
- overall: your holistic score, not necessarily the average of the above

Then give:
- feedback: 2-4 sentences of direct, specific feedback
- improvements: 2-4 concrete, actionable suggestions

Respond with ONLY a JSON object matching exactly this shape (no extra keys):
{json.dumps(_OUTPUT_SCHEMA, indent=2)}
"""
