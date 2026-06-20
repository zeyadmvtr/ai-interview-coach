"""
Application-specific exceptions and the FastAPI handlers that turn them
into clean JSON error responses instead of raw 500 stack traces.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for all expected, handled application errors."""

    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ResumeParsingError(AppError):
    status_code = 422


class JobDescriptionParsingError(AppError):
    status_code = 422


class OllamaServiceError(AppError):
    """Raised when the local Ollama/Qwen service is unreachable or returns
    a malformed response."""

    status_code = 502


class TranscriptionError(AppError):
    status_code = 422


class InvalidFileError(AppError):
    status_code = 415


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "InternalServerError", "detail": "An unexpected error occurred."},
        )
