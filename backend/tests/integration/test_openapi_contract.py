import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_committed_openapi_is_up_to_date() -> None:
    # Load the script itself so the test and the generator can never disagree on formatting.
    spec = importlib.util.spec_from_file_location("export_openapi", ROOT / "scripts" / "export_openapi.py")
    assert spec is not None and spec.loader is not None
    export = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(export)

    committed = (ROOT / "openapi.json").read_text()
    assert committed == export.render_openapi(), (
        f"openapi.json is stale. Regenerate it with: {export.REGEN_COMMAND}  (then commit the result)"
    )
