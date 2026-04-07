from __future__ import annotations

from collections.abc import AsyncIterator
import json
from time import perf_counter
from typing import Any

import httpx

from app.contracts import ChatMessage, GenerationOptions, HealthStatus, ProviderHealth, TokenUsage
from app.core.errors import ModelNotFoundError, ProviderUnavailableError, RequestTimeoutError
from app.modules.llm.base import BaseLLMProvider


class LocalOllamaProvider(BaseLLMProvider):
    provider_name = "ollama"

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: int,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def complete(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
    ) -> tuple[str, TokenUsage | None]:
        payload = self._build_chat_payload(messages, options, stream=False)

        response_json = await self._request_json("POST", "/api/chat", json=payload)
        message = response_json.get("message", {})
        content = message.get("content")

        if not isinstance(content, str) or not content:
            raise ProviderUnavailableError("Ollama returned an empty completion response.")

        return content, self._extract_usage(response_json)

    async def stream_complete(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
    ) -> AsyncIterator[str]:
        payload = self._build_chat_payload(messages, options, stream=True)

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            try:
                async with client.stream("POST", "/api/chat", json=payload) as response:
                    self._raise_for_status(response)

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError as exc:
                            raise ProviderUnavailableError(
                                "Ollama returned an invalid streaming response."
                            ) from exc

                        if "error" in chunk:
                            raise ProviderUnavailableError(str(chunk["error"]))

                        message = chunk.get("message", {})
                        content = message.get("content")
                        if isinstance(content, str) and content:
                            yield content

                        if chunk.get("done") is True:
                            break
            except httpx.TimeoutException as exc:
                raise RequestTimeoutError(
                    f"Ollama stream request timed out after {self.timeout_seconds} seconds."
                ) from exc
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(f"Failed to stream from Ollama: {exc}") from exc

    async def list_models(self) -> list[dict]:
        response_json = await self._request_json("GET", "/api/tags")
        models = response_json.get("models")

        if not isinstance(models, list):
            raise ProviderUnavailableError("Ollama returned an invalid model list response.")

        return [model for model in models if isinstance(model, dict)]

    async def health_check(self) -> ProviderHealth:
        start = perf_counter()

        try:
            models = await self.list_models()
        except (ProviderUnavailableError, RequestTimeoutError) as exc:
            return ProviderHealth(
                provider=self.provider_name,
                available=False,
                status=HealthStatus.UNAVAILABLE,
                message=str(exc),
            )

        latency_ms = round((perf_counter() - start) * 1000, 2)
        model_names = {model.get("name") for model in models if isinstance(model.get("name"), str)}

        if self.model in model_names:
            return ProviderHealth(
                provider=self.provider_name,
                available=True,
                status=HealthStatus.HEALTHY,
                latency_ms=latency_ms,
                message=f"Configured model '{self.model}' is available.",
            )

        return ProviderHealth(
            provider=self.provider_name,
            available=True,
            status=HealthStatus.DEGRADED,
            latency_ms=latency_ms,
            message=f"Configured model '{self.model}' was not found in Ollama.",
        )

    def _build_chat_payload(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
        *,
        stream: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "stream": stream,
            "options": {
                "temperature": options.temperature,
            },
        }

        if options.max_tokens is not None:
            payload["options"]["num_predict"] = options.max_tokens
        if options.top_p is not None:
            payload["options"]["top_p"] = options.top_p

        return payload

    async def _request_json(
        self,
        method: str,
        path: str,
        **request_kwargs: Any,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            try:
                response = await client.request(method, path, **request_kwargs)
                self._raise_for_status(response)
            except httpx.TimeoutException as exc:
                raise RequestTimeoutError(
                    f"Ollama request timed out after {self.timeout_seconds} seconds."
                ) from exc
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(f"Failed to call Ollama: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ProviderUnavailableError("Ollama returned an invalid JSON response.") from exc
        if not isinstance(payload, dict):
            raise ProviderUnavailableError("Ollama returned a non-object JSON response.")

        return payload

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        detail = self._extract_error_message(response)
        if response.status_code == 404 and "not found" in detail.lower():
            raise ModelNotFoundError(detail)
        if response.status_code == 408:
            raise RequestTimeoutError(detail)

        raise ProviderUnavailableError(detail)

    def _extract_error_message(self, response: httpx.Response) -> str:
        default_message = f"Ollama request failed with status {response.status_code}."

        try:
            payload = response.json()
        except ValueError:
            return default_message

        if isinstance(payload, dict):
            error_message = payload.get("error")
            if isinstance(error_message, str) and error_message:
                return error_message

        return default_message

    def _extract_usage(self, payload: dict[str, Any]) -> TokenUsage | None:
        prompt_tokens = payload.get("prompt_eval_count")
        completion_tokens = payload.get("eval_count")

        if not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int):
            return None

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
