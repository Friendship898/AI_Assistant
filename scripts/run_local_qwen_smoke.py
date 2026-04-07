from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "services" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.contracts import ChatMessage, GenerationOptions
from app.modules.llm import ProviderFactory

DEFAULT_MODEL_DIR = Path(r"D:\AI\Models\Qwen3-14B")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a single local Qwen3 smoke prompt against a Hugging Face model directory."
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Path to the local Hugging Face model directory.",
    )
    parser.add_argument(
        "--prompt",
        default="Explain what a large language model is in two short sentences.",
        help="Prompt to send to the local model.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=96,
        help="Maximum number of new tokens to generate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    model_dir = args.model_dir.resolve()

    if not model_dir.exists():
        print(f"Model directory does not exist: {model_dir}", file=sys.stderr)
        return 1

    provider = ProviderFactory.create_local(
        "huggingface_local",
        {
            "model": "Qwen3-14B",
            "model_path": str(model_dir),
            "dtype": "auto",
            "enable_thinking": False,
            "timeout_seconds": 60,
        },
    )
    print(f"Loading backend provider from: {model_dir}")

    content, usage = asyncio.run(
        provider.complete(
            [
                ChatMessage(
                    id="smoke-user-1",
                    role="user",
                    content=args.prompt,
                    created_at=datetime.now(timezone.utc),
                )
            ],
            GenerationOptions(max_tokens=args.max_new_tokens, temperature=0.7, top_p=0.8),
        )
    )

    print("=== Prompt ===")
    print(args.prompt)
    print("=== Response ===")
    print(content)
    if usage is not None:
        print("=== Usage ===")
        print(
            f"prompt_tokens={usage.prompt_tokens} "
            f"completion_tokens={usage.completion_tokens} "
            f"total_tokens={usage.total_tokens}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
