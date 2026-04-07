from pathlib import Path


def normalize_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()

