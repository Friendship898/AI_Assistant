from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Desktop Assistant Backend"
    app_version: str = "0.1.0"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    log_level: str = "INFO"
    local_llm_provider: str = "huggingface_local"
    local_llm_base_url: str = "http://127.0.0.1:11434"
    local_llm_model: str = "Qwen3-14B"
    local_llm_model_path: str = r"D:\AI\Models\Qwen3-14B"
    local_llm_timeout_seconds: int = 60
    local_llm_dtype: str = "auto"
    local_llm_enable_thinking: bool = False
    cors_allowed_origins: list[str] = [
        "http://127.0.0.1:1420",
        "http://localhost:1420",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

