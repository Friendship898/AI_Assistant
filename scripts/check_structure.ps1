$ErrorActionPreference = "Stop"

$requiredPaths = @(
    "apps/desktop/package.json",
    "apps/desktop/src/App.tsx",
    "apps/desktop/src-tauri/Cargo.toml",
    "apps/desktop/src-tauri/src/lib.rs",
    "services/backend/pyproject.toml",
    "services/backend/app/main.py",
    "services/backend/app/core/config.py",
    "services/backend/app/modules/router/__init__.py",
    "services/backend/app/modules/llm/__init__.py",
    "services/backend/app/modules/tools/__init__.py",
    "services/backend/app/modules/session/__init__.py",
    "services/backend/app/modules/library/__init__.py",
    "services/backend/app/modules/actions/__init__.py",
    "shared/openapi",
    "shared/prompts",
    "scripts/dev_backend.sh",
    "scripts/dev_desktop.sh",
    "docs/ARCHITECTURE.md",
    "docs/API_CONTRACT.md"
)

$missing = @()
foreach ($path in $requiredPaths) {
    if (-not (Test-Path -LiteralPath $path)) {
        $missing += $path
    }
}

if ($missing.Count -gt 0) {
    Write-Error ("Missing Step0 paths:`n" + ($missing -join "`n"))
}

Write-Host "Step0 structure check passed."

