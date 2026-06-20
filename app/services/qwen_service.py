"""
Module 5: Qwen Service.

Single centralized client for talking to the local Ollama server running
qwen3:8b. Every LLM-backed feature in the app (resume analysis, question
generation, answer evaluation, final report) goes through this one class.
Prompts are never hardcoded here -- they live in app/prompts/ and are
imported.
"""
import httpx

from app.core.config import get_settings
from app.core.exceptions import OllamaServiceError
from app.core.logging import get_logger
from app.prompts import answer_evaluation, final_report, question_generation, resume_analysis
from app.utils.json_parser import safe_parse_json

logger = get_logger(__name__)


class QwenService:
    """Centralized wrapper around the Ollama /api/chat endpoint for qwen3:8b."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_host.rstrip("/")
        self._model = settings.ollama_model
        self._timeout = settings.ollama_timeout_seconds
        self._max_retries = settings.ollama_max_retries

    async def _chat_json(self, system_prompt: str, user_prompt: str) -> dict | list:
        """Send a chat request to Ollama, forcing JSON-mode output, with retries."""
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.3},
        }

        last_error: Exception | None = None

        for attempt in range(1, self._max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content", "")
                if not content:
                    raise OllamaServiceError("Ollama returned an empty response.")
                return safe_parse_json(content)

            except httpx.ConnectError as exc:
                last_error = exc
                logger.error(
                    "Could not connect to Ollama at %s (attempt %d/%d). Is `ollama serve` running?",
                    self._base_url,
                    attempt,
                    self._max_retries + 1,
                )
            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning("Ollama request timed out (attempt %d/%d)", attempt, self._max_retries + 1)
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.error("Ollama returned HTTP %s: %s", exc.response.status_code, exc.response.text[:300])
            except OllamaServiceError as exc:
                # Malformed JSON from the model -- worth retrying since temperature > 0.
                last_error = exc
                logger.warning("Model output failed JSON parsing (attempt %d/%d): %s", attempt, self._max_retries + 1, exc)

        raise OllamaServiceError(
            f"Failed to get a valid response from Ollama after {self._max_retries + 1} attempts: {last_error}"
        )

    async def analyze_resume(self, resume: dict, job_description: dict) -> dict:
        """Module 6: AI Resume Analysis."""
        prompt = resume_analysis.build_prompt(resume, job_description)
        result = await self._chat_json(resume_analysis.SYSTEM_PROMPT, prompt)
        return self._ensure_keys(
            result, ["strengths", "weaknesses", "missing_skills", "recommendations"]
        )

    async def generate_questions(self, resume: dict, job_description: dict, level: str) -> dict:
        """Module 7: Interview Question Generator."""
        prompt = question_generation.build_prompt(resume, job_description, level)
        result = await self._chat_json(question_generation.SYSTEM_PROMPT, prompt)
        return self._ensure_keys(result, ["behavioral", "technical", "project_based"])

    async def evaluate_answer(
        self, question: str, answer: str, resume: dict, job_description: dict
    ) -> dict:
        """Module 9: Answer Evaluation."""
        prompt = answer_evaluation.build_prompt(question, answer, resume, job_description)
        result = await self._chat_json(answer_evaluation.SYSTEM_PROMPT, prompt)
        result = self._ensure_keys(
            result,
            [
                "technical",
                "communication",
                "relevance",
                "completeness",
                "confidence",
                "overall",
                "feedback",
                "improvements",
            ],
        )
        for key in ("technical", "communication", "relevance", "completeness", "confidence", "overall"):
            result[key] = max(0.0, min(10.0, float(result[key])))
        return result

    async def generate_final_report(self, evaluations: list[dict], averages: dict) -> dict:
        """Module 10: Final Interview Report (qualitative portion only)."""
        prompt = final_report.build_prompt(evaluations, averages)
        result = await self._chat_json(final_report.SYSTEM_PROMPT, prompt)
        return self._ensure_keys(result, ["strong_areas", "weak_areas", "final_recommendation"])

    @staticmethod
    def _ensure_keys(result: dict | list, required_keys: list[str]) -> dict:
        if not isinstance(result, dict):
            raise OllamaServiceError(f"Expected a JSON object from the model, got: {type(result).__name__}")
        missing = [k for k in required_keys if k not in result]
        if missing:
            raise OllamaServiceError(f"Model response is missing required keys: {missing}")
        return result
