from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.export_openapi import build_openapi_schema


def test_health_contract_is_exposed_in_openapi() -> None:
    schema = build_openapi_schema()

    assert "/api/v1/health" in schema["paths"]
    assert schema["paths"]["/api/v1/health"]["get"]["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"] == "#/components/schemas/HealthApiResponse"
    assert schema["components"]["schemas"]["HealthStatus"]["enum"] == [
        "healthy",
        "degraded",
        "unavailable",
    ]


def test_chat_contracts_are_exported_into_openapi_components() -> None:
    schema = build_openapi_schema()
    components = schema["components"]["schemas"]

    assert "ChatRequest" in components
    assert "ChatResponse" in components
    assert "RouteResult" in components
    assert "ContextItem" in components
    assert "ChatMessage" in components
    assert "GenerationOptions" in components
    assert "TokenUsage" in components
    assert components["RequestedMode"]["enum"] == ["auto", "local", "remote", "hybrid"]
    assert components["ExecutionMode"]["enum"] == ["local", "remote", "hybrid"]
