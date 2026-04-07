from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.contracts.common import ChatMessage, ContextItem, GenerationOptions, TokenUsage
from app.contracts.enums import ExecutionMode, PrivacyLevel, RequestedMode, TaskType, ToolName


class ChatRequest(BaseModel):
    session_id: str | None = None
    query: str
    requested_mode: RequestedMode = RequestedMode.AUTO
    context_items: list[ContextItem] = Field(default_factory=list)
    history: list[ChatMessage] = Field(default_factory=list)
    options: GenerationOptions = Field(default_factory=GenerationOptions)


class RouteResult(BaseModel):
    execution_mode: ExecutionMode
    reason_code: str
    reason_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    task_type: TaskType
    privacy_level: PrivacyLevel
    planned_tools: list[ToolName] = Field(default_factory=list)
    requires_confirmation: bool = False
    confirmation_message: str | None = None
    selected_provider: str
    selected_model: str
    context_summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    reply: ChatMessage
    route_result: RouteResult
    usage: TokenUsage | None = None
