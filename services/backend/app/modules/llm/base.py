from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.contracts import ChatMessage, GenerationOptions, ProviderHealth, TokenUsage


class BaseLLMProvider(ABC):
    provider_name: str

    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
    ) -> tuple[str, TokenUsage | None]:
        ...

    @abstractmethod
    async def stream_complete(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
    ) -> AsyncIterator[str]:
        ...

    @abstractmethod
    async def list_models(self) -> list[dict]:
        ...

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        ...
