"""
Desktop launcher regression tests for CineMatrix Studio.

Guards the release-bundle launch path: the packaged ``dist_release/`` ships a
prebuilt ``frontend_dist/`` and no ``frontend/`` source tree, so the launcher
must serve the interface itself instead of shelling out to ``npm run dev``.
"""
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

import desktop_launcher  # type: ignore  # noqa: E402
import main  # type: ignore  # noqa: E402

SHIPPED_LAUNCH_FILES = ["desktop_launcher.py", "start_cinematrix.bat"]


def test_launcher_version_is_single_sourced():
    assert desktop_launcher.APP_VERSION == main.APP_VERSION
    assert desktop_launcher.USER_AGENT.endswith(f"/{main.APP_VERSION}")


@pytest.mark.parametrize("filename", SHIPPED_LAUNCH_FILES)
def test_shipped_launch_files_do_not_hardcode_versions(filename):
    source = (ROOT_DIR / filename).read_text(encoding="utf-8")
    assert not re.search(r"(?i)\bv\d+\.\d+\b", source), f"{filename} hardcodes a vX.Y version"
    assert not re.search(r"CineMatrixDesktop/\d", source), f"{filename} hardcodes the User-Agent version"


def test_onboarding_guide_header_matches_release_line():
    header = (ROOT_DIR / "SCREENWRITER_ONBOARDING_GUIDE.md").read_text(encoding="utf-8").splitlines()[0]
    major_minor = ".".join(main.APP_VERSION.split(".")[:2])
    assert f"v{major_minor}" in header


def test_batch_launcher_needs_python_only():
    bat = (ROOT_DIR / "start_cinematrix.bat").read_text(encoding="utf-8")
    assert "npm" not in bat.lower(), "release bundle must not require Node.js / npm"
    assert "requirements.txt" in bat, "first run must install backend dependencies"
    assert "(3, 12) <= sys.version_info[:2] <= (3, 14)" in bat, "Python range must match the verified 3.12-3.14 set"
    assert "py -%%V" in bat, "should prefer supported versions via the py launcher over PATH python"


def test_batch_launcher_uses_crlf_line_endings():
    raw = (ROOT_DIR / "start_cinematrix.bat").read_bytes()
    assert b"\n" in raw
    assert raw.count(b"\n") == raw.count(b"\r\n"), "cmd.exe mis-parses labels in LF-only batch files"


def test_detect_frontend_mode(tmp_path):
    assert desktop_launcher.detect_frontend_mode(str(tmp_path)) is None

    bundle = tmp_path / "bundle"
    (bundle / "frontend_dist").mkdir(parents=True)
    (bundle / "frontend_dist" / "index.html").write_text("<div id=\"root\"></div>")
    assert desktop_launcher.detect_frontend_mode(str(bundle)) == "bundled"

    checkout = tmp_path / "checkout"
    (checkout / "frontend").mkdir(parents=True)
    (checkout / "frontend" / "package.json").write_text("{}")
    assert desktop_launcher.detect_frontend_mode(str(checkout)) == "development"

    assert desktop_launcher.detect_frontend_mode(str(ROOT_DIR)) == "development"


@pytest.fixture
def bundled_server(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text(
        '<!DOCTYPE html><div id="root"></div><script type="module" src="/assets/app-abc.js"></script>',
        encoding="utf-8",
    )
    (tmp_path / "assets" / "app-abc.js").write_text("export const ok = true;\n", encoding="utf-8")
    (tmp_path / "assets" / "app-abc.css").write_text("body{}\n", encoding="utf-8")

    server = desktop_launcher.serve_bundled_frontend(str(tmp_path), host="127.0.0.1", port=0)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        yield base
    finally:
        server.shutdown()
        server.server_close()
        desktop_launcher.servers.remove(server)


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, resp.headers, resp.read()


def test_bundled_server_serves_index_with_no_cache(bundled_server):
    status, headers, body = _get(bundled_server + "/")
    assert status == 200
    assert b'id="root"' in body
    assert headers.get("Cache-Control") == "no-cache"


@pytest.mark.parametrize(
    "asset, expected_type",
    [("/assets/app-abc.js", "text/javascript"), ("/assets/app-abc.css", "text/css")],
)
def test_bundled_server_pins_module_mime_types(bundled_server, asset, expected_type):
    status, headers, _ = _get(bundled_server + asset)
    assert status == 200
    assert headers.get("Content-Type", "").startswith(expected_type)


def test_bundled_server_falls_back_to_index_for_client_routes(bundled_server):
    status, _, body = _get(bundled_server + "/studio/storyboard")
    assert status == 200
    assert b'id="root"' in body


def test_bundled_server_404s_missing_assets(bundled_server):
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        _get(bundled_server + "/assets/missing.js")
    assert excinfo.value.code == 404


def test_bundled_server_blocks_path_traversal(bundled_server, tmp_path):
    secret = tmp_path.parent / "cinematrix_secret.txt"
    secret.write_text("do-not-serve", encoding="utf-8")
    try:
        for path in ("/../cinematrix_secret.txt", "/%2e%2e/cinematrix_secret.txt"):
            try:
                _, _, body = _get(bundled_server + path)
            except urllib.error.HTTPError:
                continue
            assert b"do-not-serve" not in body
    finally:
        secret.unlink()


@pytest.mark.skipif(os.name != "nt", reason="SO_REUSEADDR port hijacking is Windows-specific")
def test_bundled_server_refuses_occupied_port_on_windows(bundled_server):
    port = int(bundled_server.rsplit(":", 1)[1])
    with pytest.raises(OSError):
        desktop_launcher.serve_bundled_frontend(str(ROOT_DIR), host="127.0.0.1", port=port)


class _FakeProcess:
    def __init__(self, returncode):
        self.returncode = returncode

    def poll(self):
        return self.returncode


def test_owned_backend_exited_tracks_launcher_started_backend(monkeypatch):
    monkeypatch.setattr(desktop_launcher, "backend_processes", [])
    assert desktop_launcher.owned_backend_exited() is False

    monkeypatch.setattr(desktop_launcher, "backend_processes", [_FakeProcess(None)])
    assert desktop_launcher.owned_backend_exited() is False

    monkeypatch.setattr(desktop_launcher, "backend_processes", [_FakeProcess(0)])
    assert desktop_launcher.owned_backend_exited() is True


def test_wait_for_interrupt_returns_when_backend_stops(monkeypatch):
    monkeypatch.setattr(desktop_launcher, "backend_processes", [_FakeProcess(0)])
    monkeypatch.setattr(desktop_launcher.time, "sleep", lambda _: pytest.fail("should not keep waiting"))
    desktop_launcher.wait_for_interrupt()


def test_favicon_reference_resolves_to_a_shipped_file():
    html = (ROOT_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    icons = re.findall(r'<link[^>]*rel="icon"[^>]*href="/([^"]+)"', html)
    assert icons, "index.html must declare a page icon"
    for icon in icons:
        assert (ROOT_DIR / "frontend" / "public" / icon).is_file(), f"/{icon} is not in frontend/public"


@pytest.mark.parametrize("relative", ["frontend/src/App.tsx", "frontend/src/components/ShutdownModal.tsx"])
def test_shutdown_restart_instructions_name_the_real_launcher(relative):
    source = (ROOT_DIR / relative).read_text(encoding="utf-8")
    for script in re.findall(r"\b([\w-]+\.bat)\b", source):
        assert (ROOT_DIR / script).is_file(), f"{relative} tells users to run {script}, which does not exist"
