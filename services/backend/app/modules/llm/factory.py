from __future__ import annotations

from app.core.errors import ConfigurationError
from app.modules.llm.base import BaseLLMProvider
from app.modules.llm.local_hf import LocalHuggingFaceProvider
from app.modules.llm.local_ollama import LocalOllamaProvider


class ProviderFactory:
    @staticmethod
    def create_local(provider_name: str, config: dict) -> BaseLLMProvider:
        if provider_name == "ollama":
            return LocalOllamaProvider(
                base_url=str(config["base_url"]),
                model=str(config["model"]),
                timeout_seconds=int(config["timeout_seconds"]),
            )

        if provider_name in {"huggingface_local", "hf_local"}:
            return LocalHuggingFaceProvider(
                model_name=str(config["model"]),
                model_path=str(config["model_path"]),
                dtype=str(config.get("dtype", "auto")),
                enable_thinking=bool(config.get("enable_thinking", False)),
                timeout_seconds=int(config["timeout_seconds"]),
            )

        raise ConfigurationError(f"Unsupported local provider '{provider_name}'.")

    @staticmethod
    def create_remote(provider_name: str, config: dict) -> BaseLLMProvider:
        raise ConfigurationError(
            f"Remote provider '{provider_name}' is not implemented in Step4."
        )
