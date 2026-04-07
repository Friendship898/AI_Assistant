from fastapi.testclient import TestClient

from app.contracts import HealthStatus, ProviderHealth
from app.main import create_app
from app.modules.llm import ProviderFactory


class StubLocalProvider:
    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider="huggingface_local",
            available=True,
            status=HealthStatus.HEALTHY,
            latency_ms=12.4,
            message="Loaded local model 'Qwen3-14B' from 'D:\\AI\\Models\\Qwen3-14B'.",
        )


def test_health_endpoint_returns_unified_response(monkeypatch) -> None:
    monkeypatch.setattr(
        ProviderFactory,
        "create_local",
        lambda provider_name, config: StubLocalProvider(),
    )
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["x-request-id"]

    payload = response.json()

    assert payload["success"] is True
    assert payload["error"] is None
    assert payload["request_id"]
    assert payload["timestamp"]
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["version"] == "0.1.0"
    assert payload["data"]["timestamp"]
    assert payload["data"]["services"]["backend"] == {
        "provider": "backend",
        "available": True,
        "status": "healthy",
        "latency_ms": None,
        "message": "FastAPI service is running.",
    }
    assert payload["data"]["services"]["local_llm"] == {
        "provider": "huggingface_local",
        "available": True,
        "status": "healthy",
        "latency_ms": 12.4,
        "message": "Loaded local model 'Qwen3-14B' from 'D:\\AI\\Models\\Qwen3-14B'.",
    }


def test_health_endpoint_reuses_incoming_request_id(monkeypatch) -> None:
    monkeypatch.setattr(
        ProviderFactory,
        "create_local",
        lambda provider_name, config: StubLocalProvider(),
    )
    client = TestClient(create_app())

    response = client.get("/api/v1/health", headers={"X-Request-ID": "health-smoke-test"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "health-smoke-test"
    assert response.json()["request_id"] == "health-smoke-test"
