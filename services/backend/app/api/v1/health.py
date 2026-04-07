from datetime import datetime, timezone

from fastapi import APIRouter, Request, status
import structlog

from app.contracts import HealthApiResponse, HealthResponse, HealthStatus, ProviderHealth
from app.core.config import get_settings
from app.core.responses import build_response
from app.modules.llm import ProviderFactory

router = APIRouter(tags=["health"])
logger = structlog.get_logger("backend.api.health")


def _resolve_overall_status(services: dict[str, ProviderHealth]) -> HealthStatus:
    statuses = {service.status for service in services.values()}
    if HealthStatus.UNAVAILABLE in statuses:
        return HealthStatus.UNAVAILABLE
    if HealthStatus.DEGRADED in statuses:
        return HealthStatus.DEGRADED
    return HealthStatus.HEALTHY


@router.get("/health", response_model=HealthApiResponse, status_code=status.HTTP_200_OK)
async def get_health(request: Request) -> HealthApiResponse:
    settings = get_settings()
    services: dict[str, ProviderHealth] = {
        "backend": ProviderHealth(
            provider="backend",
            available=True,
            status=HealthStatus.HEALTHY,
            message="FastAPI service is running.",
        )
    }

    try:
        local_provider = ProviderFactory.create_local(
            settings.local_llm_provider,
            {
                "base_url": settings.local_llm_base_url,
                "model": settings.local_llm_model,
                "model_path": settings.local_llm_model_path,
                "timeout_seconds": settings.local_llm_timeout_seconds,
                "dtype": settings.local_llm_dtype,
                "enable_thinking": settings.local_llm_enable_thinking,
            },
        )
        services["local_llm"] = await local_provider.health_check()
    except Exception as exc:
        logger.error("local_llm_health_failed", error=str(exc), provider=settings.local_llm_provider)
        services["local_llm"] = ProviderHealth(
            provider=settings.local_llm_provider,
            available=False,
            status=HealthStatus.UNAVAILABLE,
            message=str(exc),
        )

    health = HealthResponse(
        status=_resolve_overall_status(services),
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        services=services,
    )
    return build_response(success=True, data=health, request=request)
