# API Contract Status

## Public Endpoint

The first public backend endpoint remains:

- `GET /api/v1/health`

## Step3

Shared chat/session DTOs are now defined even though no public chat endpoint has been added yet.

## Step5

The health payload now includes local provider runtime status under `data.services.local_llm`.

## Contract Source of Truth

The backend contract source directory is:

- `services/backend/app/contracts/`

Current Step5 state:

- backend health and common response contracts live under `services/backend/app/contracts/`
- OpenAPI can be exported to `shared/openapi/openapi.json`
- frontend TypeScript types are generated from that OpenAPI schema
- chat/session DTO contracts now include `ContextItem`, `ChatMessage`, `GenerationOptions`, `TokenUsage`, `ChatRequest`, `RouteResult`, and `ChatResponse`
- `ProviderHealth` is used for both `backend` and `local_llm` service entries in `/api/v1/health`
- local provider health can report `healthy`, `degraded`, or `unavailable`

This step adds local provider health reporting and local runtime generation readiness only. It does not add `/api/v1/chat`, remote providers, routing behavior, tools, or persistence behavior yet.

