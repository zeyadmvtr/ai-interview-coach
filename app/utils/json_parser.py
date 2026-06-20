"""
LLMs occasionally wrap JSON in markdown code fences, add a leading
'Here is the JSON:' sentence, or include trailing commentary. This module
extracts and parses the JSON object defensively so the rest of the app
never has to deal with raw LLM text.
"""
import json
import re

from app.core.exceptions import OllamaServiceError


def extract_json_block(text: str) -> str:
    """Pull the first {...} or [...] block out of a raw LLM response."""
    text = text.strip()

    # Strip ```json ... ``` or ``` ... ``` fences if present.
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # Fall back to locating the outermost JSON object/array by brace matching.
    start_chars = "{["
    for i, ch in enumerate(text):
        if ch in start_chars:
            open_ch = ch
            close_ch = "}" if ch == "{" else "]"
            depth = 0
            for j in range(i, len(text)):
                if text[j] == open_ch:
                    depth += 1
                elif text[j] == close_ch:
                    depth -= 1
                    if depth == 0:
                        return text[i : j + 1]
            break

    return text


def safe_parse_json(text: str) -> dict | list:
    """Parse LLM output into a Python object, raising OllamaServiceError
    with the offending text if it truly isn't valid JSON."""
    candidate = extract_json_block(text)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise OllamaServiceError(
            f"Model did not return valid JSON: {exc}. Raw output: {text[:500]!r}"
        ) from exc
