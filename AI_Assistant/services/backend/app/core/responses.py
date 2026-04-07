from datetime import datetime, timezone
from typing import Any


def build_response(
    *,
    success: bool,
    data: Any | None = None,
    error: dict[str, Any] | None = None,
    request_id: str = "step0-placeholder",
) -> dict[str, Any]:
    return {
        "success": success,
        "data": data,
        "error": error,
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

