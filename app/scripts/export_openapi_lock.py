from __future__ import annotations

import json
from pathlib import Path

from app.main import app


def export_openapi_lock(output_path: str = "openapi.lock.json") -> Path:
    target = Path(output_path)
    schema = app.openapi()
    target.write_text(json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return target


if __name__ == "__main__":
    path = export_openapi_lock()
    print(f"OpenAPI lock escrito em: {path}")
