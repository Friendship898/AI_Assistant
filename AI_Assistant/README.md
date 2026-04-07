# AI Desktop Assistant

This repository contains the Step0 project skeleton for the AI desktop assistant defined in [docs/EXECUTION_MANUAL.md](/C:/Users/Administrator/Desktop/AI_Assistant/docs/EXECUTION_MANUAL.md) and [docs/CODEX_STEPS.md](/C:/Users/Administrator/Desktop/AI_Assistant/docs/CODEX_STEPS.md).

## Current Status

- `apps/desktop`: React 18 + TypeScript + Tauri v2 desktop shell scaffold.
- `services/backend`: FastAPI backend scaffold with config and logging bootstrap.
- `scripts`: local development entry scripts plus a Step0 structure checker.

Step0 intentionally does **not** include health checks, chat, tools, routing rules, or model integration yet.

## Repository Layout

```text
apps/desktop        Desktop UI shell
services/backend    Backend API shell
shared/openapi      Generated schemas output directory
shared/prompts      Shared prompt assets directory
scripts             Local development helper scripts
```

## Local Run

Once the required runtimes are installed:

```bash
./scripts/dev_backend.sh
./scripts/dev_desktop.sh
```

For a quick structure check in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_structure.ps1
```

## Next Recommended Step

Implement Step1: `GET /api/v1/health` with a unified response wrapper and backend smoke tests.

