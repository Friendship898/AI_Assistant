from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_step0_backend_files_exist() -> None:
    required_paths = [
        PROJECT_ROOT / "services/backend/app/main.py",
        PROJECT_ROOT / "services/backend/app/core/config.py",
        PROJECT_ROOT / "services/backend/app/core/logging.py",
        PROJECT_ROOT / "services/backend/app/api/router.py",
        PROJECT_ROOT / "services/backend/pyproject.toml",
        PROJECT_ROOT / "services/backend/config.yaml",
        PROJECT_ROOT / "scripts/dev_backend.sh",
    ]

    missing = [path for path in required_paths if not path.exists()]
    assert not missing, f"Missing Step0 backend files: {missing}"

