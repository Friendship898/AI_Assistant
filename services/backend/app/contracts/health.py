from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.contracts.common import ApiResponse
from app.contracts.enums import HealthStatus


class ProviderHealth(BaseModel):
    provider: str
    available: bool
    status: HealthStatus
    latency_ms: float | None = None
    message: str | None = None


class HealthResponse(BaseModel):
    status: HealthStatus
    version: str
    timestamp: datetime
    services: dict[str, ProviderHealth]


class HealthApiResponse(ApiResponse[HealthResponse]):
    pass
