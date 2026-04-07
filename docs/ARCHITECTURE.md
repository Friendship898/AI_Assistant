# Architecture Overview

## Step5 Scope

The repository is bootstrapped around a two-process local architecture:

- `apps/desktop`: Tauri v2 hosts the desktop shell, React renders the UI.
- `services/backend`: a single FastAPI process will host all backend modules.

## Boundaries

- Desktop business requests will eventually go through HTTP/SSE to the backend.
- Tauri commands are reserved for system capability bridges only.
- Backend modules remain logical boundaries inside one Python service.

## Current Implementation

The repository now exposes the first public backend endpoint, keeps contracts as the schema source of truth, and adds a local provider module for runtime health checks:

- frontend entry files
- Tauri Rust entry files
- backend app factory, config, and logging bootstrap
- backend `app/contracts/` as the schema source of truth
- shared DTO definitions for context items, chat messages, chat requests, route results, and chat responses
- exported OpenAPI schema under `shared/openapi/`
- generated frontend TypeScript types consumed by the desktop shell
- `GET /api/v1/health` with a unified response envelope
- backend `modules/llm/` provider abstraction plus `local_hf.py` as the default local runtime adapter
- health endpoint aggregation for `backend` and `local_llm`
- desktop UI rendering of backend and local provider status
- placeholder module packages for future steps

No chat endpoint, routing execution, tool execution, or persistence behavior is exposed yet beyond the health check, DTO/contract sync path, and local provider runtime integration.

