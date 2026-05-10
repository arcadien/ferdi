"""
Acceptance tests for BRQ-003 — Screen screenshot command (SPEC-011).
"""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from ferdi.main import app
from ferdi.screenshot import capture_screen

client = TestClient(app)


# --- Endpoint ---


def test_brq003_snapshot_endpoint_exists():
    """POST /screenshot endpoint must exist and accept requests."""
    response = client.post("/screenshot")
    assert response.status_code in [200, 400, 500], (
        "POST /screenshot endpoint must exist"
    )


def test_brq003_returns_200_with_json_body():
    """POST /screenshot must return HTTP 200 with JSON body."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        response = client.post("/screenshot")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_brq003_response_message():
    """POST /screenshot must return {"message": "screen is shot"}."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        response = client.post("/screenshot")
    assert response.json() == {"message": "screen is shot"}


# --- capture_screen() function ---


def test_brq003_capture_screen_is_reusable_function():
    """capture_screen() must be importable and callable directly."""
    assert callable(capture_screen)


def test_brq003_capture_screen_returns_path():
    """capture_screen() must return a Path object pointing to the saved file."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        result = capture_screen()
    assert isinstance(result, Path)
    assert result.exists()


def test_brq003_capture_screen_saves_png_file():
    """capture_screen() must save the image as a PNG file."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        result = capture_screen()
    assert result.suffix == ".png"
    assert result.exists()


def test_brq003_capture_screen_creates_screenshots_directory():
    """capture_screen() must create screenshots/ if it does not exist."""
    screenshots_dir = Path("screenshots")
    if screenshots_dir.exists():
        for file in screenshots_dir.glob("*"):
            file.unlink()
        screenshots_dir.rmdir()
    assert not screenshots_dir.exists()

    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        capture_screen()

    assert screenshots_dir.exists()


def test_brq003_screenshots_dir_created_automatically():
    """POST /screenshot must create screenshots/ if it does not exist."""
    screenshots_dir = Path("screenshots")
    if screenshots_dir.exists():
        for file in screenshots_dir.glob("*"):
            file.unlink()
        screenshots_dir.rmdir()
    assert not screenshots_dir.exists()

    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        response = client.post("/screenshot")

    assert response.status_code == 200
    assert screenshots_dir.exists()


def test_brq003_capture_screen_uses_imagegrab():
    """capture_screen() must call PIL.ImageGrab.grab() exactly once."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        capture_screen()
    mock_grab.assert_called_once()


def test_brq003_capture_screen_calls_image_save():
    """capture_screen() must call image.save() on the captured image."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_image = MagicMock()
        mock_grab.return_value = mock_image
        capture_screen()
    mock_image.save.assert_called_once()


def test_brq003_multiple_screenshots_each_save_a_file():
    """Multiple POST /screenshot calls must each save a distinct file."""
    with patch("ferdi.screenshot.ImageGrab.grab") as mock_grab:
        mock_grab.return_value = MagicMock()
        client.post("/screenshot")
        time.sleep(0.1)
        client.post("/screenshot")

    screenshots = list(Path("screenshots").glob("*.png"))
    assert len(screenshots) >= 2
