from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from app.contracts.enums import ContextSource

ResponseDataT = TypeVar("ResponseDataT")


class ErrorDetail(BaseModel):
    code: str
    message: str
    suggestion: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel, Generic[ResponseDataT]):
    success: bool
    data: ResponseDataT | None = None
    error: ErrorDetail | None = None
    request_id: str
    timestamp: datetime


class ContextItem(BaseModel):
    id: str
    source: ContextSource
    name: str | None = None
    mime_type: str | None = None
    text_content: str | None = None
    file_path: str | None = None
    binary_ref: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    id: str
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationOptions(BaseModel):
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float | None = None
    stream: bool = False


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
