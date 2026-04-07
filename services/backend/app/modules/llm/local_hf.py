from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from time import perf_counter
from types import SimpleNamespace
from typing import Any

from app.contracts import ChatMessage, GenerationOptions, HealthStatus, ProviderHealth, TokenUsage
from app.core.errors import ProviderUnavailableError
from app.modules.llm.base import BaseLLMProvider


@dataclass(slots=True)
class _RuntimeBundle:
    model: Any
    tokenizer: Any
    torch: Any
    device: Any


class LocalHuggingFaceProvider(BaseLLMProvider):
    provider_name = "huggingface_local"
    _runtime_lock = Lock()
    _runtime_cache: dict[str, _RuntimeBundle] = {}

    def __init__(
        self,
        *,
        model_name: str,
        model_path: str,
        dtype: str,
        enable_thinking: bool,
        timeout_seconds: int,
    ) -> None:
        self.model_name = model_name
        self.model_path = Path(model_path)
        self.dtype = dtype
        self.enable_thinking = enable_thinking
        self.timeout_seconds = timeout_seconds

    async def complete(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
    ) -> tuple[str, TokenUsage | None]:
        return await asyncio.to_thread(self._complete_sync, messages, options)

    async def stream_complete(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
    ) -> AsyncIterator[str]:
        content, _usage = await self.complete(messages, options)
        yield content

    async def list_models(self) -> list[dict]:
        runtime_state = "loaded" if self.model_path.as_posix() in self._runtime_cache else "ready"
        return [
            {
                "name": self.model_name,
                "path": str(self.model_path),
                "provider": self.provider_name,
                "state": runtime_state,
            }
        ]

    async def health_check(self) -> ProviderHealth:
        start = perf_counter()

        try:
            await asyncio.to_thread(self._ensure_runtime_loaded_sync)
        except ProviderUnavailableError as exc:
            return ProviderHealth(
                provider=self.provider_name,
                available=False,
                status=HealthStatus.UNAVAILABLE,
                message=str(exc),
            )

        latency_ms = round((perf_counter() - start) * 1000, 2)
        return ProviderHealth(
            provider=self.provider_name,
            available=True,
            status=HealthStatus.HEALTHY,
            latency_ms=latency_ms,
            message=f"Loaded local model '{self.model_name}' from '{self.model_path}'.",
        )

    def _complete_sync(
        self,
        messages: list[ChatMessage],
        options: GenerationOptions,
    ) -> tuple[str, TokenUsage | None]:
        runtime = self._ensure_runtime_loaded_sync()
        prompt_text = runtime.tokenizer.apply_chat_template(
            [{"role": message.role, "content": message.content} for message in messages],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=self.enable_thinking,
        )
        model_inputs = runtime.tokenizer([prompt_text], return_tensors="pt").to(runtime.device)

        generation_kwargs: dict[str, Any] = {
            "max_new_tokens": options.max_tokens or 256,
            "pad_token_id": runtime.tokenizer.eos_token_id or runtime.tokenizer.pad_token_id,
        }

        if options.temperature <= 0:
            generation_kwargs["do_sample"] = False
        else:
            generation_kwargs["do_sample"] = True
            generation_kwargs["temperature"] = options.temperature
            if options.top_p is not None:
                generation_kwargs["top_p"] = options.top_p

        with runtime.torch.inference_mode():
            generated_ids = runtime.model.generate(**model_inputs, **generation_kwargs)

        input_token_count = int(model_inputs.input_ids.shape[-1])
        output_ids = generated_ids[0][input_token_count:]
        completion_token_count = int(output_ids.shape[-1])
        content = runtime.tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        if not content:
            raise ProviderUnavailableError("The local Hugging Face model returned an empty response.")

        return (
            content,
            TokenUsage(
                prompt_tokens=input_token_count,
                completion_tokens=completion_token_count,
                total_tokens=input_token_count + completion_token_count,
            ),
        )

    def _ensure_runtime_loaded_sync(self) -> _RuntimeBundle:
        cache_key = self.model_path.as_posix()

        cached_runtime = self._runtime_cache.get(cache_key)
        if cached_runtime is not None:
            return cached_runtime

        with self._runtime_lock:
            cached_runtime = self._runtime_cache.get(cache_key)
            if cached_runtime is not None:
                return cached_runtime

            self._validate_model_directory()
            torch_module, transformers_module = self._import_runtime_dependencies()
            tokenizer = transformers_module.AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            model = transformers_module.AutoModelForCausalLM.from_pretrained(
                self.model_path,
                local_files_only=True,
                dtype=self._resolve_dtype(torch_module),
                device_map="auto" if torch_module.cuda.is_available() else None,
                low_cpu_mem_usage=True,
            )
            model.eval()
            device = getattr(model, "device", None)
            if device is None:
                device = next(model.parameters()).device
            runtime = _RuntimeBundle(
                model=model,
                tokenizer=tokenizer,
                torch=torch_module,
                device=device,
            )
            self._runtime_cache[cache_key] = runtime
            return runtime

    def _validate_model_directory(self) -> None:
        if not self.model_path.exists():
            raise ProviderUnavailableError(
                f"Local model directory does not exist: {self.model_path}"
            )
        required_paths = [
            self.model_path / "config.json",
            self.model_path / "tokenizer.json",
            self.model_path / "model.safetensors.index.json",
        ]
        missing_paths = [path.name for path in required_paths if not path.exists()]
        if missing_paths:
            raise ProviderUnavailableError(
                f"Local model directory is missing required files: {', '.join(missing_paths)}"
            )

    def _import_runtime_dependencies(self) -> tuple[Any, Any]:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise ProviderUnavailableError(
                "Missing local Hugging Face runtime dependencies. Install torch, transformers, accelerate, and safetensors."
            ) from exc

        return torch, SimpleNamespace(
            AutoModelForCausalLM=AutoModelForCausalLM,
            AutoTokenizer=AutoTokenizer,
        )

    def _resolve_dtype(self, torch_module: Any) -> Any:
        normalized = self.dtype.lower()
        if normalized == "bfloat16":
            return torch_module.bfloat16
        if normalized == "float16":
            return torch_module.float16
        if normalized == "float32":
            return torch_module.float32
        if torch_module.cuda.is_available():
            return torch_module.bfloat16
        return torch_module.float32
