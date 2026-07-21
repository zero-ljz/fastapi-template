"""Export the FastAPI OpenAPI document for frontend type generation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else BACKEND_ROOT / "openapi.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OpenAPI document written to {output}")


if __name__ == "__main__":
    main()
