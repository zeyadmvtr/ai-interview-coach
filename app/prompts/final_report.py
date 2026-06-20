"""Prompt for Module 10: Final Interview Report (QwenService.generate_final_report).

Numeric averages (overall_score, technical_average, etc.) are computed
deterministically in Python -- they must not depend on the LLM. This prompt
only asks the model for the qualitative summary: strong_areas, weak_areas,
and a final hire/no-hire-style recommendation narrative.
"""
import json

SYSTEM_PROMPT = (
    "You are a senior hiring panel lead summarizing a candidate's full interview "
    "performance for the hiring team. You are direct and evidence-based. You "
    "ALWAYS respond with a single valid JSON object and nothing else -- no "
    "markdown fences, no preamble."
)

_OUTPUT_SCHEMA = {
    "strong_areas": ["string"],
    "weak_areas": ["string"],
    "final_recommendation": "string, 3-5 sentences",
}


def build_prompt(evaluations: list[dict], averages: dict) -> str:
    return f"""Summarize this candidate's full interview performance.

PER-QUESTION EVALUATIONS:
{json.dumps(evaluations, indent=2)}

COMPUTED AVERAGES:
{json.dumps(averages, indent=2)}

Based on the evaluations above, produce:
- strong_areas: 2-5 specific areas where the candidate consistently performed well
- weak_areas: 2-5 specific areas where the candidate consistently struggled
- final_recommendation: a 3-5 sentence overall recommendation (e.g. strong hire,
  hire with reservations, no hire) with clear reasoning tied to the evidence above.
  Do not just restate the numbers -- explain what they mean.

Respond with ONLY a JSON object matching exactly this shape (no extra keys):
{json.dumps(_OUTPUT_SCHEMA, indent=2)}
"""
