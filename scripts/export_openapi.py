"""Write the API contract to <repo root>/openapi.json (the frontend generates its types from it).

Usage: backend/.venv/bin/python scripts/export_openapi.py
Sorted keys + 2-space indent + trailing newline keep the file diff-stable, so
`git diff --exit-code openapi.json` and tests/integration/test_openapi_contract.py can detect drift.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "openapi.json"
REGEN_COMMAND = "backend/.venv/bin/python scripts/export_openapi.py"


def render_openapi() -> str:
    # Imported lazily: the backend package lives in backend/, not on sys.path by default.
    sys.path.insert(0, str(ROOT / "backend"))
    from app.main import create_app

    # create_app() only builds a lazy engine, so no database is needed to export the schema.
    return json.dumps(create_app().openapi(), sort_keys=True, indent=2) + "\n"


def main() -> None:
    OUTPUT.write_text(render_openapi())
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
