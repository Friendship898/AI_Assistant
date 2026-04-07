# Lessons Learned

## Purpose

This document records environment setup and repository hygiene lessons that came up during this project, and is intended to be reused on future projects to avoid repeating the same mistakes.

## Universal Setup Checklist

Before installing anything:

1. Read `README.md` and all setup-related files under `docs/`.
2. Extract the exact runtime requirements:
   - language runtime versions
   - package managers
   - build toolchains
   - OS-specific prerequisites
3. Check whether the repository already contains:
   - `.gitignore`
   - required empty directories
   - lockfiles
   - local run scripts
4. Check the machine state before installing:
   - `git`
   - language runtimes
   - package managers
   - native build tools
5. Only then install project dependencies.

## Reusable Rules

### 1. Separate environment problems from repository problems

Do not assume a failed run means the machine is missing tools. First determine whether the issue is:

- missing system runtime or toolchain
- missing project dependency installation
- repository structure defect
- broken test or build configuration

This project had all four categories at once.

### 2. Always add ignore rules before installing large dependencies

Installations created large local folders such as:

- `node_modules`
- `.venv`
- build output directories
- Rust `target`

If `.gitignore` is missing, create it before `npm install`, `pip install`, or builds. Otherwise thousands of generated files enter Git status and make the repository noisy and risky to upload.

Minimum ignore categories for most app projects:

- Node dependencies and build output
- Python virtual environments and caches
- Rust build output
- logs
- editor/system files

### 3. Preserve required empty directories explicitly

If docs or scripts require empty directories such as generated-contract folders, Git will not keep them unless placeholder files exist.

Use `.gitkeep` or another agreed placeholder file for directories that must exist but may be empty.

This project needed:

- `shared/openapi/`
- `shared/prompts/`

### 4. Verify shell assumptions on Windows

This repository provided `.sh` scripts, but the active shell was PowerShell.

Common Windows pitfalls:

- PowerShell execution policy can block `npm.ps1`
- `.sh` scripts assume Git Bash, WSL, or another POSIX shell
- newly installed tools may not appear in the current shell `PATH` immediately

Practical rule:

- on Windows, prefer explicit executable paths when needed, such as `npm.cmd`
- verify whether Bash is available before relying on `.sh` scripts
- if a tool was just installed, verify with the absolute path if `PATH` has not refreshed yet

### 5. Install in dependency order, not convenience order

For desktop apps with frontend + backend + native shell, the stable order is:

1. language runtimes
2. native compiler toolchains
3. OS runtime prerequisites
4. project dependencies
5. structure checks
6. tests
7. build validation

For this project the effective order was:

1. Python 3.11
2. Rust toolchain
3. Visual Studio Build Tools
4. WebView2 Runtime
5. frontend dependencies
6. backend virtual environment and dependencies
7. repository structure fixes
8. tests and builds

### 6. Expect tests to reveal project defects after setup succeeds

A successful environment install does not mean the repository is healthy.

This project still had two repository issues after setup:

- frontend test config did not expose Vitest globals
- backend layout test computed the wrong project root

Rule:

- after dependency installation, run tests immediately
- treat test failures as codebase issues unless they clearly indicate a missing runtime

### 7. Distinguish “tool installed” from “tool usable”

Validation should include:

- version check
- invocation in the project
- at least one real build or test command

Examples from this project:

- `tauri --version` alone was not enough; `cargo check` and frontend build were also needed
- Python being installed was not enough; the backend had to import and run under the intended version

## Recommended Preflight Commands

For a new project, run a quick preflight like:

```powershell
git --version
node --version
npm --version
py --version
cargo --version
rustc --version
```

Then check project-local status:

```powershell
git status --short
```

And confirm required files and folders from docs before installing anything.

## Session Record

### 2026-04-07

Project: `AI Desktop Assistant`

Observed issues:

- repository had no `.gitignore`
- required empty directories were missing
- Python 3.11 was not installed
- Rust toolchain was not installed
- Visual C++ build tools were not available
- WebView2 runtime was not installed
- frontend dependencies were not installed
- backend virtual environment was not created
- PowerShell could not directly use `npm` because of execution policy
- two tests failed due to repository configuration/code issues, not environment issues

Actions that resolved the situation:

- installed the missing runtimes and build tools
- installed frontend and backend dependencies
- added `.gitignore`
- added `.gitkeep` files for required empty directories
- fixed the frontend test configuration
- fixed the backend test path calculation

## Future Entry Template

When updating this document for future projects, append an entry using:

```md
### YYYY-MM-DD

Project: `<name>`

Observed issues:

- issue 1
- issue 2

Actions that resolved the situation:

- action 1
- action 2

What should be done earlier next time:

- prevention 1
- prevention 2
```
