"""
Acceptance tests for BRQ-003 — Screen snapshot command (SPEC-011).

These tests are written before the implementation exists and are expected to
fail (RED) until the POST /snapshot endpoint and capture_screen() function are
implemented in ferdi/main.py and ferdi/screenshot.py.
"""

import re
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from ferdi.main import app  # noqa: E402 — will fail until implementation exists
from ferdi.screenshot import capture_screen  # noqa: E402 — will fail until implementation exists

client = TestClient(app)


# --- Acceptance Criterion 1: POST /snapshot endpoint exists ---

def test_brq003_snapshot_endpoint_exists():
    """POST /snapshot endpoint must exist and accept requests."""
    response = client.post("/snapshot")
    # Accept any status code (200 or error) — the endpoint must exist
    assert response.status_code in [200, 400, 500], "POST /snapshot endpoint must exist"


# --- Acceptance Criterion 2: Returns HTTP 200 with JSON body containing path field ---

def test_brq003_returns_200_with_json_body():
    """POST /snapshot must return HTTP 200 with JSON body."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response = client.post("/snapshot")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_brq003_response_contains_path_field():
    """POST /snapshot response JSON must contain a 'path' field."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response = client.post("/snapshot")

    assert response.status_code == 200
    data = response.json()
    assert "path" in data, "Response JSON must contain 'path' field"
    assert isinstance(data["path"], str), "'path' field must be a string"


# --- Acceptance Criterion 3: Path matches format screenshots/YYYY-MM-DD_HH-MM-SS.png ---

def test_brq003_path_matches_timestamp_format():
    """The 'path' field must match format screenshots/YYYY-MM-DD_HH-MM-SS.png."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response = client.post("/snapshot")

    assert response.status_code == 200
    data = response.json()
    path = data["path"]

    # Verify format: screenshots/YYYY-MM-DD_HH-MM-SS.png
    pattern = r"^screenshots/\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.png$"
    assert re.match(pattern, path), (
        f"Path '{path}' must match format 'screenshots/YYYY-MM-DD_HH-MM-SS.png'"
    )


def test_brq003_path_timestamp_is_parseable():
    """The timestamp in the path must be a valid datetime string."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response = client.post("/snapshot")

    assert response.status_code == 200
    data = response.json()
    path = data["path"]

    # Extract timestamp from path: screenshots/YYYY-MM-DD_HH-MM-SS.png
    match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", path)
    assert match, "Path must contain a valid timestamp"

    timestamp_str = match.group(1)
    # Must be parseable with %Y-%m-%d_%H-%M-%S format
    try:
        datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        assert False, f"Timestamp '{timestamp_str}' cannot be parsed with format '%Y-%m-%d_%H-%M-%S'"


# --- Acceptance Criterion 4: Screenshot file exists on disk after call ---

def test_brq003_file_exists_on_disk_after_call():
    """The screenshot file must exist on disk after POST /snapshot returns."""
    # Use real filesystem, mock only ImageGrab
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response = client.post("/snapshot")

    assert response.status_code == 200
    data = response.json()
    file_path = Path(data["path"])

    # File must exist
    assert file_path.exists(), f"File {file_path} must exist on disk after POST /snapshot"
    assert file_path.is_file(), f"{file_path} must be a regular file"


# --- Acceptance Criterion 5: screenshots/ directory created automatically if absent ---

def test_brq003_screenshots_dir_created_automatically():
    """The screenshots/ directory must be created automatically if it does not exist."""
    # Ensure directory is deleted before test
    screenshots_dir = Path("screenshots")
    if screenshots_dir.exists():
        # Delete all files in the directory first
        for file in screenshots_dir.glob("*"):
            file.unlink()
        screenshots_dir.rmdir()

    assert not screenshots_dir.exists(), "screenshots/ directory must not exist before test"

    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response = client.post("/snapshot")

    assert response.status_code == 200
    assert screenshots_dir.exists(), "screenshots/ directory must be created automatically"
    assert screenshots_dir.is_dir(), "screenshots/ must be a directory"


# --- Acceptance Criterion 6: Capture logic is a reusable function ---

def test_brq003_capture_screen_is_reusable_function():
    """The capture_screen() function must be importable and callable directly."""
    # Should be importable (we already did this at the top)
    assert callable(capture_screen), "capture_screen must be callable"


def test_brq003_capture_screen_returns_path():
    """capture_screen() must return a Path object pointing to the saved file."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        result = capture_screen()

    assert isinstance(result, Path), "capture_screen() must return a Path object"
    assert result.exists(), "Returned path must point to an existing file"


def test_brq003_capture_screen_saves_png_file():
    """capture_screen() must save the image as a PNG file."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        result = capture_screen()

    assert result.suffix == ".png", "Saved file must have .png extension"
    assert result.exists(), "PNG file must exist after capture_screen()"


def test_brq003_capture_screen_creates_screenshots_directory():
    """capture_screen() must create the screenshots/ directory if it does not exist."""
    # Clean up directory
    screenshots_dir = Path("screenshots")
    if screenshots_dir.exists():
        for file in screenshots_dir.glob("*"):
            file.unlink()
        screenshots_dir.rmdir()

    assert not screenshots_dir.exists(), "screenshots/ directory must not exist before test"

    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        capture_screen()

    assert screenshots_dir.exists(), "capture_screen() must create screenshots/ directory"


def test_brq003_capture_screen_uses_imagegrab():
    """capture_screen() must use PIL.ImageGrab.grab() to capture the screen."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        capture_screen()

    mock_grab.assert_called_once(), "ImageGrab.grab() must be called exactly once"


def test_brq003_capture_screen_calls_image_save():
    """capture_screen() must call image.save() on the captured image."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        capture_screen()

    mock_image.save.assert_called_once(), "image.save() must be called exactly once"


# --- Additional integration tests ---

def test_brq003_multiple_snapshots_have_different_filenames():
    """Multiple consecutive snapshots must have different filenames (different timestamps)."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response1 = client.post("/snapshot")
        # Ensure timestamp differs (small sleep)
        import time
        time.sleep(0.1)
        response2 = client.post("/snapshot")

    assert response1.status_code == 200
    assert response2.status_code == 200

    path1 = response1.json()["path"]
    path2 = response2.json()["path"]

    assert path1 != path2, "Multiple snapshots must have different filenames"


def test_brq003_endpoint_returns_relative_path():
    """The returned path must be a relative path (relative to project root)."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image

        response = client.post("/snapshot")

    assert response.status_code == 200
    path = response.json()["path"]

    # Path must start with screenshots/, not be absolute
    assert not Path(path).is_absolute(), "Path must be relative (not absolute)"
    assert path.startswith("screenshots/"), "Path must start with 'screenshots/'"
