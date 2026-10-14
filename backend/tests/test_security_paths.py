"""
Security regression tests for CineMatrix Studio.

Covers the sample-script path-traversal fix (arbitrary file read via the
`category` / `filename` fields of the example-loading endpoints) and the
backend dependency contract that keeps the API bootable.
"""
import os
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app  # type: ignore
from examples_service import EXAMPLES_BASE_DIR, resolve_example_path  # type: ignore

client = TestClient(app)

TRAVERSAL_PAIRS = [
    ("../..", "README.md"),
    ("../../..", "Projects"),
    ("formats/../../..", "README.md"),
    ("formats", "../../../README.md"),
]


@pytest.mark.parametrize("category,filename", TRAVERSAL_PAIRS)
def test_resolve_example_path_rejects_traversal(category, filename):
    with pytest.raises(ValueError):
        resolve_example_path(category, filename)


@pytest.mark.parametrize("part", ["C:\\Windows\\win.ini", "/etc/passwd", "\\server\\share"])
def test_resolve_example_path_rejects_absolute_paths(part):
    with pytest.raises(ValueError):
        resolve_example_path("formats", part)


def test_resolve_example_path_allows_catalog_file():
    resolved = resolve_example_path("formats", "01_screenplay_hollywood.fountain")
    assert resolved.startswith(os.path.realpath(EXAMPLES_BASE_DIR))
    assert os.path.exists(resolved)


def test_load_example_rejects_traversal_payload():
    project = client.post("/projects", json={"name": "sec", "description": "sec"})
    assert project.status_code == 200
    project_id = project.json()["id"]

    resp = client.post(
        f"/projects/{project_id}/load-example",
        json={"category": "../..", "filename": "README.md"},
    )
    assert resp.status_code == 400
    assert "Invalid example script path" in resp.text

    client.delete(f"/projects/{project_id}")


def test_create_with_example_rejects_traversal_payload():
    resp = client.post(
        "/projects/create-with-example",
        json={"category": "../..", "filename": "README.md"},
    )
    assert resp.status_code == 400


def test_required_runtime_imports_are_declared():
    """The API imports these at module load; a missing pin breaks startup."""
    req_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    with open(req_path, "r", encoding="utf-8-sig") as handle:
        declared = [
            line.strip().lower()
            for line in handle
            if line.strip() and not line.strip().startswith("#")
        ]
    requirements = "\n".join(declared)

    for package in ("opencv-python", "numpy", "google-genai", "pymupdf", "pypdf"):
        assert package in requirements, f"{package} missing from requirements.txt"

    assert not any(line.startswith("google-generativeai") for line in declared), (
        "legacy google-generativeai SDK must not be declared; "
        "providers/google_provider.py uses the google-genai SDK"
    )


def test_api_version_is_single_sourced():
    import main  # type: ignore

    assert app.version == main.APP_VERSION
    assert client.get("/health").json()["version"] == main.APP_VERSION
    assert client.get("/").json()["version"] == main.APP_VERSION


def test_desktop_build_version_matches_app_version():
    """The desktop release manifest must not drift from backend APP_VERSION."""
    import main  # type: ignore

    root_dir = Path(__file__).resolve().parents[2]
    source = (root_dir / "build_desktop.py").read_text(encoding="utf-8")
    match = re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', (root_dir / "backend" / "main.py").read_text(encoding="utf-8"), re.MULTILINE)

    assert match is not None and match.group(1) == main.APP_VERSION
    assert "read_app_version()" in source, "build_desktop.py must derive its version from backend/main.py"
    assert not re.search(r'"version":\s*"\d+\.\d+\.\d+"', source), "build_desktop.py must not hardcode a version"
    assert not re.search(r"CineMatrix Studio v\d+\.\d+", source), "build output must not hardcode a version"

    sys.path.insert(0, str(root_dir))
    import build_desktop  # type: ignore

    ignored = build_desktop.backend_copy_ignore(
        str(root_dir / "backend"),
        ["database", "tests", "storyboard.db", ".env", "main.py"],
    )
    assert ignored == {"tests", "storyboard.db", ".env"}

    media_ignored = build_desktop.backend_copy_ignore(
        str(root_dir / "backend" / "static" / "videos"),
        [".gitkeep", "generated.mp4"],
    )
    assert media_ignored == {"generated.mp4"}
