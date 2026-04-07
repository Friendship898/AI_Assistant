# Architecture Overview

## Step0 Scope

The repository is bootstrapped around a two-process local architecture:

- `apps/desktop`: Tauri v2 hosts the desktop shell, React renders the UI.
- `services/backend`: a single FastAPI process will host all backend modules.

## Boundaries

- Desktop business requests will eventually go through HTTP/SSE to the backend.
- Tauri commands are reserved for system capability bridges only.
- Backend modules remain logical boundaries inside one Python service.

## Current Implementation

Step0 provides only the minimum startup shell:

- frontend entry files
- Tauri Rust entry files
- backend app factory, config, and logging bootstrap
- placeholder module packages for future steps

No business API contract is exposed yet beyond framework bootstrap defaults.

