"""
Centralized application configuration.

All environment-dependent values are read here, once, via pydantic-settings.
Nothing else in the codebase should call os.getenv() directly.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    # Ollama / Qwen
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"
    ollama_timeout_seconds: float = 120.0
    ollama_max_retries: int = 2

    # Faster Whisper
    whisper_model_size: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    # Uploads
    max_upload_size_mb: int = 10


@lru_cache
def get_settings() -> Settings:
    """Settings are cheap to build but we still cache a single instance."""
    return Settings()
