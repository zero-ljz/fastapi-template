"""导出 OpenAPI 文档以生成前端接口类型。"""

import json
import sys
from pathlib import Path

from app.main import app


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("openapi.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OpenAPI 文档已写入 {output}")


if __name__ == "__main__":
    main()
