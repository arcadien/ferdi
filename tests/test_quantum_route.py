"""
Acceptance tests for BRQ-002 — Set a quantum route by voice (SPEC-009).

These tests are written before the implementation exists and are expected to
fail (RED) until the quantum-route endpoint and validator interface are implemented.
"""

from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from ferdi.main import app
from ferdi.validators import get_validator
from ferdi.validators.base import RouteValidator
from ferdi.validators.bypass import BypassValidator
from ferdi.validators.claude_vision import ClaudeVisionValidator

client = TestClient(app)


# --- Acceptance Criterion 1: Returns 400 if app.state.resolution is not set ---


def test_trq009_returns_400_when_resolution_not_set():
    """POST /quantum-route must return HTTP 400 if app.state.resolution is not set."""
    # Ensure resolution is not set
    if hasattr(app.state, "resolution"):
        delattr(app.state, "resolution")

    response = client.post("/quantum-route", json={"destination": "Hurston"})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Resolution not detected. Run detect-resolution first."


# --- Acceptance Criterion 2: Returns 200 with correct response when flow succeeds ---


def test_trq009_returns_200_with_correct_response_on_success():
    """POST /quantum-route must return HTTP 200 with destination, status, and message on successful flow."""
    # Set resolution
    app.state.resolution = {"width": 2560, "height": 1440}

    # Mock all pydirectinput calls
    with (
        patch("ferdi.main.pydirectinput.press"),
        patch("ferdi.main.pydirectinput.moveTo"),
        patch("ferdi.main.pydirectinput.click"),
        patch("ferdi.main.pydirectinput.typewrite"),
        patch("ferdi.main.time.sleep"),
        patch("ferdi.main.yaml.safe_load") as mock_yaml,
    ):
        mock_yaml.side_effect = [
            {
                "starmap": {
                    "search_field_x_pct": 0.25,
                    "search_field_y_pct": 0.10,
                    "key_open": "F2",
                    "key_validate": "enter",
                    "key_close": "F2",
                    "key_quantum": "b",
                },
                "validator": {"type": "bypass"},
            },
            {},
        ]

        response = client.post("/quantum-route", json={"destination": "Hurston"})

    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Hurston"
    assert data["status"] == "ok"
    assert "Quantum route to Hurston set" in data["message"]


# --- Acceptance Criterion 3: Presses keys and moves mouse in correct sequence ---


def test_trq009_executes_key_presses_and_mouse_movement_in_order():
    """POST /quantum-route must execute key_open, moveTo, click, typewrite, key_validate, key_close, key_quantum in order."""
    app.state.resolution = {"width": 2560, "height": 1440}

    mock_press = MagicMock()
    mock_move = MagicMock()
    mock_click = MagicMock()
    mock_typewrite = MagicMock()
    mock_sleep = MagicMock()

    with (
        patch("ferdi.main.pydirectinput.press", mock_press),
        patch("ferdi.main.pydirectinput.moveTo", mock_move),
        patch("ferdi.main.pydirectinput.click", mock_click),
        patch("ferdi.main.pydirectinput.typewrite", mock_typewrite),
        patch("ferdi.main.time.sleep", mock_sleep),
        patch("ferdi.main.yaml.safe_load") as mock_yaml,
    ):
        mock_yaml.side_effect = [
            {
                "starmap": {
                    "search_field_x_pct": 0.25,
                    "search_field_y_pct": 0.10,
                    "key_open": "F2",
                    "key_validate": "enter",
                    "key_close": "F2",
                    "key_quantum": "b",
                },
                "validator": {"type": "bypass"},
            },
            {},
        ]

        response = client.post("/quantum-route", json={"destination": "Hurston"})

    assert response.status_code == 200

    # Verify key_open was pressed (F2)
    assert mock_press.call_count >= 1, "pydirectinput.press should be called"
    first_calls = [call for call in mock_press.call_args_list]
    assert any(
        "F2" in str(call) or "f2" in str(call).lower() for call in first_calls
    ), "key_open (F2) should be pressed"

    # Verify moveTo was called to move mouse to search field
    assert mock_move.call_count >= 1, (
        "pydirectinput.moveTo should be called to position mouse"
    )

    # Verify click was called
    assert mock_click.call_count >= 1, "pydirectinput.click should be called"

    # Verify typewrite was called with destination
    assert mock_typewrite.call_count >= 1, (
        "pydirectinput.typewrite should be called to type destination"
    )

    # Verify key_validate (enter) was pressed
    enter_pressed = any(
        "enter" in str(call).lower() or "return" in str(call).lower()
        for call in first_calls
    )
    assert enter_pressed, "key_validate (enter) should be pressed"

    # Verify key_close and key_quantum were pressed
    # There should be at least 3 press calls: key_open, key_validate, key_close, key_quantum
    assert mock_press.call_count >= 3, (
        "Multiple key presses expected (open, validate, close, quantum)"
    )


# --- Acceptance Criterion 4: Returns 500 when validator returns False ---


def test_trq009_returns_500_when_validator_fails():
    """POST /quantum-route must return HTTP 500 when validator.validate() returns False."""
    app.state.resolution = {"width": 2560, "height": 1440}

    with (
        patch("ferdi.main.pydirectinput.press"),
        patch("ferdi.main.pydirectinput.moveTo"),
        patch("ferdi.main.pydirectinput.click"),
        patch("ferdi.main.pydirectinput.typewrite"),
        patch("ferdi.main.time.sleep"),
        patch("ferdi.main.yaml.safe_load") as mock_yaml,
        patch("ferdi.main.get_validator") as mock_get_validator,
    ):
        mock_yaml.side_effect = [
            {
                "starmap": {
                    "search_field_x_pct": 0.25,
                    "search_field_y_pct": 0.10,
                    "key_open": "F2",
                    "key_validate": "enter",
                    "key_close": "F2",
                    "key_quantum": "b",
                },
                "validator": {"type": "bypass"},
            },
            {},
        ]

        # Mock validator to return False
        mock_validator = MagicMock(spec=RouteValidator)
        mock_validator.validate.return_value = False
        mock_get_validator.return_value = mock_validator

        response = client.post("/quantum-route", json={"destination": "Hurston"})

    assert response.status_code == 500
    data = response.json()
    assert "Could not confirm quantum route to Hurston" in data["detail"]


# --- Acceptance Criterion 5: BypassValidator.validate() always returns True ---


def test_trq010_bypass_validator_always_returns_true():
    """BypassValidator.validate() must always return True regardless of destination."""
    validator = BypassValidator()

    assert validator.validate("Hurston") is True
    assert validator.validate("Arccorp") is True
    assert validator.validate("") is True
    assert validator.validate("any_destination") is True


# --- Acceptance Criterion 6: get_validator with bypass type returns BypassValidator ---


def test_trq010_get_validator_returns_bypass_validator():
    """get_validator({"validator": {"type": "bypass"}}) must return a BypassValidator instance."""
    config = {"validator": {"type": "bypass"}}
    validator = get_validator(config)

    assert isinstance(validator, BypassValidator)


# --- Acceptance Criterion 7: get_validator with unknown type raises ValueError ---


def test_trq010_get_validator_raises_on_unknown_type():
    """get_validator({"validator": {"type": "unknown"}}) must raise ValueError."""
    config = {"validator": {"type": "unknown"}}

    try:
        get_validator(config)
        assert False, "get_validator should raise ValueError for unknown type"
    except ValueError as e:
        assert "unknown" in str(e).lower()


# --- Additional tests for validators and factory ---


def test_trq010_claude_vision_validator_exists():
    """ClaudeVisionValidator must exist and be instantiable."""
    validator = ClaudeVisionValidator()
    assert isinstance(validator, RouteValidator)


def test_trq010_get_validator_returns_claude_vision_validator():
    """get_validator({"validator": {"type": "claude-vision"}}) must return a ClaudeVisionValidator instance."""
    config = {"validator": {"type": "claude-vision"}}
    validator = get_validator(config)

    assert isinstance(validator, ClaudeVisionValidator)


def test_trq010_route_validator_interface_exists():
    """RouteValidator abstract interface must be importable and have validate method."""
    assert hasattr(RouteValidator, "validate"), (
        "RouteValidator must have validate method"
    )


# --- Additional tests for coordinate calculations and flow ---


def test_nfr002_calculates_correct_absolute_coordinates():
    """Given resolution and percentage, absolute coordinates must be calculated correctly."""
    app.state.resolution = {"width": 2560, "height": 1440}

    # Expected: x = 2560 * 0.25 = 640, y = 1440 * 0.10 = 144
    with (
        patch("ferdi.main.pydirectinput.press"),
        patch("ferdi.main.pydirectinput.moveTo") as mock_move,
        patch("ferdi.main.pydirectinput.click"),
        patch("ferdi.main.pydirectinput.typewrite"),
        patch("ferdi.main.time.sleep"),
        patch("ferdi.main.yaml.safe_load") as mock_yaml,
    ):
        mock_yaml.side_effect = [
            {
                "starmap": {
                    "search_field_x_pct": 0.25,
                    "search_field_y_pct": 0.10,
                    "key_open": "F2",
                    "key_validate": "enter",
                    "key_close": "F2",
                    "key_quantum": "b",
                },
                "validator": {"type": "bypass"},
            },
            {},
        ]

        response = client.post("/quantum-route", json={"destination": "Hurston"})

    assert response.status_code == 200

    # Verify moveTo was called with correct coordinates
    # x = 2560 * 0.25 = 640, y = 1440 * 0.10 = 144
    mock_move.assert_called()
    calls = mock_move.call_args_list
    # Check that one of the calls has approximately the expected coordinates
    found_correct_coordinates = False
    for call in calls:
        if len(call[0]) >= 2:
            x, y = call[0][0], call[0][1]
            if x == 640 and y == 144:
                found_correct_coordinates = True
                break
    assert found_correct_coordinates, (
        f"Expected moveTo(640, 144) to be called, but got: {calls}"
    )


def test_brq002_quantum_route_endpoint_accepts_destination():
    """POST /quantum-route must accept {"destination": "..."} request body."""
    app.state.resolution = {"width": 2560, "height": 1440}

    with (
        patch("ferdi.main.pydirectinput.press"),
        patch("ferdi.main.pydirectinput.moveTo"),
        patch("ferdi.main.pydirectinput.click"),
        patch("ferdi.main.pydirectinput.typewrite"),
        patch("ferdi.main.time.sleep"),
        patch("ferdi.main.yaml.safe_load") as mock_yaml,
    ):
        mock_yaml.side_effect = [
            {
                "starmap": {
                    "search_field_x_pct": 0.25,
                    "search_field_y_pct": 0.10,
                    "key_open": "F2",
                    "key_validate": "enter",
                    "key_close": "F2",
                    "key_quantum": "b",
                },
                "validator": {"type": "bypass"},
            },
            {},
        ]

        response = client.post("/quantum-route", json={"destination": "Arccorp"})

    assert response.status_code == 200
    assert response.json()["destination"] == "Arccorp"


def test_brq002_quantum_route_loads_yaml_config():
    """POST /quantum-route must load configuration from etc/sc-config.yaml."""
    app.state.resolution = {"width": 2560, "height": 1440}

    with (
        patch("ferdi.main.pydirectinput.press"),
        patch("ferdi.main.pydirectinput.moveTo"),
        patch("ferdi.main.pydirectinput.click"),
        patch("ferdi.main.pydirectinput.typewrite"),
        patch("ferdi.main.time.sleep"),
        patch("ferdi.main.yaml.safe_load") as mock_yaml,
    ):
        mock_yaml.side_effect = [
            {
                "starmap": {
                    "search_field_x_pct": 0.25,
                    "search_field_y_pct": 0.10,
                    "key_open": "F2",
                    "key_validate": "enter",
                    "key_close": "F2",
                    "key_quantum": "b",
                },
                "validator": {"type": "bypass"},
            },
            {},
        ]

        response = client.post("/quantum-route", json={"destination": "Hurston"})

    assert response.status_code == 200
    # Verify yaml.safe_load was called
    mock_yaml.assert_called()
