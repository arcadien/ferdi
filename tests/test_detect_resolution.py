"""
Acceptance tests for BRQ-001 — Detect screen resolution (SPEC-008).

These tests are written before the implementation exists and are expected to
fail (RED) until POST /detect-resolution is implemented in ferdi/main.py.
"""

from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from ferdi.main import app  # noqa: E402 — will fail until implementation exists

client = TestClient(app)


def test_brq001_detect_resolution_returns_200_with_primary_monitor():
    """POST /detect-resolution must return HTTP 200 with width, height, and message when primary monitor exists."""
    # Mock screeninfo.get_monitors to return a primary monitor
    mock_monitor = MagicMock()
    mock_monitor.is_primary = True
    mock_monitor.width = 2560
    mock_monitor.height = 1440

    with patch("ferdi.main.screeninfo.get_monitors", return_value=[mock_monitor]):
        response = client.post("/detect-resolution")

    assert response.status_code == 200
    data = response.json()
    assert data["width"] == 2560
    assert data["height"] == 1440
    assert data["message"] == "Resolution 2560 by 1440 detected"


def test_brq001_app_state_resolution_set_on_success():
    """app.state.resolution must be set to {"width": ..., "height": ...} after successful detection."""
    mock_monitor = MagicMock()
    mock_monitor.is_primary = True
    mock_monitor.width = 1920
    mock_monitor.height = 1080

    with patch("ferdi.main.screeninfo.get_monitors", return_value=[mock_monitor]):
        response = client.post("/detect-resolution")

    assert response.status_code == 200
    # Check that app.state.resolution has been set
    assert hasattr(app.state, "resolution"), "app.state.resolution must be set"
    assert app.state.resolution == {"width": 1920, "height": 1080}, (
        "app.state.resolution must be exactly {'width': 1920, 'height': 1080}"
    )


def test_brq001_detect_resolution_returns_500_when_no_primary_monitor():
    """POST /detect-resolution must return HTTP 500 with error detail when no primary monitor is found."""
    # Mock screeninfo.get_monitors to return an empty list (no primary monitor)
    with patch("ferdi.main.screeninfo.get_monitors", return_value=[]):
        response = client.post("/detect-resolution")

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "No primary monitor found"


def test_brq001_app_state_resolution_not_modified_on_error():
    """app.state.resolution must not be modified when no primary monitor is found."""
    # Set an initial state value
    app.state.resolution = {"width": 9999, "height": 9999}

    # Mock screeninfo.get_monitors to return no primary monitor
    with patch("ferdi.main.screeninfo.get_monitors", return_value=[]):
        response = client.post("/detect-resolution")

    assert response.status_code == 500
    # The state should remain unchanged
    assert app.state.resolution == {"width": 9999, "height": 9999}, (
        "app.state.resolution must not be modified when primary monitor is not found"
    )
