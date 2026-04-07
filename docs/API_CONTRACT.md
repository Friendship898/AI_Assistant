# API Contract Status

## Step0

Step0 establishes the backend application shell only. No product API endpoints are implemented in this step.

## Reserved Next Contract

Step1 will introduce the first public endpoint:

- `GET /api/v1/health`

## Contract Source of Truth

The future shared contract source directory already exists at:

- `services/backend/app/contracts/`

Step2 will define concrete Pydantic contracts and drive frontend type generation from that source.

