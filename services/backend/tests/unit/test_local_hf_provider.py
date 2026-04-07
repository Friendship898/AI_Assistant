from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import torch

from app.contracts import ChatMessage, GenerationOptions, HealthStatus
from app.modules.llm.factory import ProviderFactory
from app.modules.llm.local_hf import LocalHuggingFaceProvider


class FakeBatch(dict):
    def __init__(self, input_ids: torch.Tensor) -> None:
        super().__init__(input_ids=input_ids)
        self.input_ids = input_ids

    def to(self, device: str) -> "FakeBatch":
        return self


class FakeTokenizer:
    eos_token_id = 99
    pad_token_id = 0

    def apply_chat_template(
        self,
        messages: list[dict[str, str]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
        enable_thinking: bool,
    ) -> str:
        assert messages == [{"role": "user", "content": "Ping"}]
        assert tokenize is False
        assert add_generation_prompt is True
        assert enable_thinking is False
        return "formatted-prompt"

    def __call__(self, prompts: list[str], *, return_tensors: str) -> FakeBatch:
        assert prompts == ["formatted-prompt"]
        assert return_tensors == "pt"
        return FakeBatch(torch.tensor([[11, 12, 13]]))

    def decode(self, output_ids: torch.Tensor, *, skip_special_tokens: bool) -> str:
        assert skip_special_tokens is True
        assert output_ids.tolist() == [14, 15]
        return "Generated reply"


class FakeModel:
    device = "cpu"

    def generate(self, **kwargs: object) -> torch.Tensor:
        assert isinstance(kwargs["input_ids"], torch.Tensor)
        assert kwargs["max_new_tokens"] == 32
        assert kwargs["do_sample"] is True
        assert kwargs["temperature"] == 0.2
        assert kwargs["top_p"] == 0.95
        return torch.tensor([[11, 12, 13, 14, 15]])


def build_provider(model_path: str) -> LocalHuggingFaceProvider:
    return LocalHuggingFaceProvider(
        model_name="Qwen3-14B",
        model_path=model_path,
        dtype="auto",
        enable_thinking=False,
        timeout_seconds=60,
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
async def test_list_models_reports_configured_local_model(tmp_path: Path) -> None:
    provider = build_provider(str(tmp_path))

    models = await provider.list_models()

    assert models == [
        {
            "name": "Qwen3-14B",
            "path": str(tmp_path),
            "provider": "huggingface_local",
            "state": "ready",
        }
    ]


@pytest.mark.asyncio
async def test_health_check_reports_unavailable_when_model_path_is_missing(tmp_path: Path) -> None:
    provider = build_provider(str(tmp_path / "missing-model"))

    health = await provider.health_check()

    assert health.provider == "huggingface_local"
    assert health.available is False
    assert health.status == HealthStatus.UNAVAILABLE
    assert "does not exist" in (health.message or "")


@pytest.mark.asyncio
async def test_health_check_reports_healthy_when_runtime_load_succeeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider = build_provider(str(tmp_path))
    monkeypatch.setattr(provider, "_ensure_runtime_loaded_sync", lambda: object())

    health = await provider.health_check()

    assert health.provider == "huggingface_local"
    assert health.available is True
    assert health.status == HealthStatus.HEALTHY
    assert health.latency_ms is not None
    assert "Loaded local model 'Qwen3-14B'" in (health.message or "")


@pytest.mark.asyncio
async def test_complete_returns_content_and_usage(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provider = build_provider(str(tmp_path))
    fake_runtime = type(
        "FakeRuntime",
        (),
        {
            "tokenizer": FakeTokenizer(),
            "model": FakeModel(),
            "torch": torch,
            "device": "cpu",
        },
    )()
    monkeypatch.setattr(provider, "_ensure_runtime_loaded_sync", lambda: fake_runtime)

    content, usage = await provider.complete(
        build_messages(),
        GenerationOptions(temperature=0.2, max_tokens=32, top_p=0.95),
    )

    assert content == "Generated reply"
    assert usage is not None
    assert usage.prompt_tokens == 3
    assert usage.completion_tokens == 2
    assert usage.total_tokens == 5


def test_factory_creates_huggingface_local_provider() -> None:
    provider = ProviderFactory.create_local(
        "huggingface_local",
        {
            "model": "Qwen3-14B",
            "model_path": r"D:\AI\Models\Qwen3-14B",
            "dtype": "auto",
            "enable_thinking": False,
            "timeout_seconds": 60,
        },
    )

    assert isinstance(provider, LocalHuggingFaceProvider)
