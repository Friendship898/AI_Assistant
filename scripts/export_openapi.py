from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "services" / "backend"
OUTPUT_PATH = REPO_ROOT / "shared" / "openapi" / "openapi.json"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app
from app.contracts import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ContextItem,
    GenerationOptions,
    RouteResult,
    TokenUsage,
)

CONTRACT_SCHEMA_MODELS = {
    "ContextItem": ContextItem,
    "ChatMessage": ChatMessage,
    "GenerationOptions": GenerationOptions,
    "TokenUsage": TokenUsage,
    "ChatRequest": ChatRequest,
    "RouteResult": RouteResult,
    "ChatResponse": ChatResponse,
}


def build_contract_component_schemas() -> dict[str, Any]:
    schemas: dict[str, Any] = {}

    for name, model in CONTRACT_SCHEMA_MODELS.items():
        model_schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
        definitions = model_schema.pop("$defs", {})

        for definition_name, definition_schema in definitions.items():
            schemas[definition_name] = definition_schema

        schemas[name] = model_schema

    return schemas


def build_openapi_schema() -> dict[str, Any]:
    schema = app.openapi()
    component_schemas = schema.setdefault("components", {}).setdefault("schemas", {})

    for name, contract_schema in build_contract_component_schemas().items():
        existing_schema = component_schemas.get(name)
        if existing_schema is not None and existing_schema != contract_schema:
            raise RuntimeError(f"OpenAPI schema conflict detected for component '{name}'.")
        component_schemas.setdefault(name, contract_schema)

    return schema


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = build_openapi_schema()
    OUTPUT_PATH.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported OpenAPI schema to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
