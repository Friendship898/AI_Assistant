from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import Request

from app.contracts import ApiResponse, ErrorDetail


def _resolve_request_id(request: Request | None, explicit_request_id: str | None) -> str:
    if explicit_request_id:
        return explicit_request_id

    if request is not None:
        request_id = getattr(request.state, "request_id", None)
        if isinstance(request_id, str) and request_id:
            return request_id

    return str(uuid4())


def build_response(
    *,
    success: bool,
    data: Any | None = None,
    error: ErrorDetail | dict[str, Any] | None = None,
    request: Request | None = None,
    request_id: str | None = None,
) -> ApiResponse[Any]:
    normalized_error = error
    if isinstance(error, dict):
        normalized_error = ErrorDetail(**error)

    return ApiResponse[Any](
        success=success,
        data=data,
        error=normalized_error,
        request_id=_resolve_request_id(request, request_id),
        timestamp=datetime.now(timezone.utc),
    )

