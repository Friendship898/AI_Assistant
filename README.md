# AI Desktop Assistant

This repository contains the current project skeleton for the AI desktop assistant defined in `docs/EXECUTION_MANUAL.md` and `docs/CODEX_STEPS.md`.

## Current Status

- `apps/desktop`: React 18 + TypeScript + Tauri v2 desktop shell consuming generated backend contract types.
- `services/backend`: FastAPI backend shell with `GET /api/v1/health`, chat/session DTO contracts, and a local Hugging Face provider adapter backed by `D:\AI\Models\Qwen3-14B`.
- `scripts`: local development scripts including OpenAPI export and TypeScript type generation.

The repository now completes Step5 by wiring the backend directly to local Hugging Face weights for runtime health reporting and local generation smoke testing. Chat endpoints, routing behavior, tools, and persistence are still pending.

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

To refresh generated contract artifacts after backend contract changes:

```bash
./scripts/generate_ts_types.sh
```

To run the current Step5 backend and desktop health flow:

```powershell
cd D:\GIT\AI_Assistant\services\backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd D:\GIT\AI_Assistant\apps\desktop
& 'C:\Program Files\nodejs\npm.cmd' run tauri dev
```

The backend defaults to `local_llm_provider=huggingface_local` and reads the model from `D:\AI\Models\Qwen3-14B`.

To validate one real local generation through the backend provider:

```powershell
& 'D:\GIT\AI_Assistant\services\backend\.venv\Scripts\python.exe' 'D:\GIT\AI_Assistant\scripts\run_local_qwen_smoke.py' --prompt '请用两句话解释什么是大型语言模型。' --max-new-tokens 80
```

## Next Recommended Step

Implement Step6: add `/api/v1/chat` on top of the existing local provider layer without introducing remote providers or tools yet.
