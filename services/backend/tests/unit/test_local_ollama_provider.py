from __future__ import annotations

from datetime import datetime, timezone
import json

import httpx
import pytest
import respx

from app.contracts import ChatMessage, GenerationOptions, HealthStatus
from app.core.errors import ModelNotFoundError
from app.modules.llm.local_ollama import LocalOllamaProvider


def build_provider() -> LocalOllamaProvider:
    return LocalOllamaProvider(
        base_url="http://127.0.0.1:11434",
        model="qwen3:14b",
        timeout_seconds=5,
    )


def build_messages() -> list[ChatMessage]:
    return [
        ChatMessage(
            id="msg-user-1",
            role="user",
            content="Ping",
            created_at=datetime.now(timezone.utc),
        )
    ]


@pytest.mark.asyncio
@respx.mock
async def test_health_check_reports_healthy_when_model_exists() -> None:
    provider = build_provider()
    route = respx.get("http://127.0.0.1:11434/api/tags").mock(
        return_value=httpx.Response(
            200,
            json={"models": [{"name": "qwen3:14b"}, {"name": "llama3.1:8b"}]},
        )
    )

    health = await provider.health_check()

    assert route.called
    assert health.provider == "ollama"
    assert health.available is True
    assert health.status == HealthStatus.HEALTHY
    assert health.latency_ms is not None
    assert "qwen3:14b" in (health.message or "")


@pytest.mark.asyncio
@respx.mock
async def test_health_check_reports_degraded_when_model_is_missing() -> None:
    provider = build_provider()
    respx.get("http://127.0.0.1:11434/api/tags").mock(
        return_value=httpx.Response(200, json={"models": [{"name": "llama3.1:8b"}]})
    )

    health = await provider.health_check()

    assert health.provider == "ollama"
    assert health.available is True
    assert health.status == HealthStatus.DEGRADED
    assert "not found" in (health.message or "").lower()


@pytest.mark.asyncio
@respx.mock
async def test_complete_returns_content_and_usage() -> None:
    provider = build_provider()
    route = respx.post("http://127.0.0.1:11434/api/chat").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": {"role": "assistant", "content": "Pong"},
                "prompt_eval_count": 8,
                "eval_count": 13,
            },
        )
    )

    content, usage = await provider.complete(
        build_messages(),
        GenerationOptions(temperature=0.2, max_tokens=32, top_p=0.95),
    )

    request_payload = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_payload["model"] == "qwen3:14b"
    assert request_payload["messages"] == [{"role": "user", "content": "Ping"}]
    assert request_payload["options"] == {
        "temperature": 0.2,
        "num_predict": 32,
        "top_p": 0.95,
    }
    assert content == "Pong"
    assert usage is not None
    assert usage.prompt_tokens == 8
    assert usage.completion_tokens == 13
    assert usage.total_tokens == 21


@pytest.mark.asyncio
@respx.mock
async def test_complete_raises_model_not_found_for_404() -> None:
    provider = build_provider()
    respx.post("http://127.0.0.1:11434/api/chat").mock(
        return_value=httpx.Response(404, json={"error": "model 'qwen3:14b' not found"})
    )

    with pytest.raises(ModelNotFoundError, match="not found"):
        await provider.complete(build_messages(), GenerationOptions())
