#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -x "${PROJECT_ROOT}/services/backend/.venv/Scripts/python.exe" ]]; then
  BACKEND_PYTHON="${PROJECT_ROOT}/services/backend/.venv/Scripts/python.exe"
elif [[ -x "${PROJECT_ROOT}/services/backend/.venv/bin/python" ]]; then
  BACKEND_PYTHON="${PROJECT_ROOT}/services/backend/.venv/bin/python"
else
  echo "Backend virtualenv Python not found." >&2
  exit 1
fi

cd "${PROJECT_ROOT}"
"${BACKEND_PYTHON}" "${PROJECT_ROOT}/scripts/export_openapi.py"

cd "${PROJECT_ROOT}/apps/desktop"
npm run generate:types
