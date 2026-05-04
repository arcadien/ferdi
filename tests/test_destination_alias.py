"""
Acceptance tests for TRQ-011 — Destination alias-to-real-name mapping (SPEC-010).

These tests verify that:
1. The POST /quantum-route endpoint looks up destination aliases in etc/qt-destinations.yaml
2. The real name (not the alias) is typed into the game search bar
3. Unknown aliases return HTTP 400 with a descriptive error message
4. The YAML file is properly loaded and used for alias resolution
"""

from unittest.mock import MagicMock, patch
import yaml

from starlette.testclient import TestClient

from ferdi.main import app

client = TestClient(app)


# --- Acceptance Criterion 1: typewrite is called with real name when alias exists ---

def test_trq011_typewrite_called_with_real_name():
    """When destination alias exists in YAML, pydirectinput.typewrite must be called with the real name (not the alias)."""
    app.state.resolution = {"width": 2560, "height": 1440}

    mock_typewrite = MagicMock()

    with patch("ferdi.main.pydirectinput.press"), \
         patch("ferdi.main.pydirectinput.moveTo"), \
         patch("ferdi.main.pydirectinput.click"), \
         patch("ferdi.main.pydirectinput.typewrite", mock_typewrite), \
         patch("ferdi.main.time.sleep"), \
         patch("ferdi.main.yaml.safe_load") as mock_yaml:

        mock_yaml.return_value = {
            "starmap": {
                "search_field_x_pct": 0.25,
                "search_field_y_pct": 0.10,
                "key_open": "F2",
                "key_validate": "enter",
                "key_close": "F2",
                "key_quantum": "b"
            },
            "validator": {"type": "bypass"},
            "destinations": {
                "Hurston L1": "HUR-L1",
                "ArcCorp L1": "ARC-L1",
                "Hurston": "Hurston"
            }
        }

        # POST with alias "Hurston L1"
        response = client.post("/quantum-route", json={"destination": "Hurston L1"})

    assert response.status_code == 200

    # Verify typewrite was called with the real name "HUR-L1", not the alias "Hurston L1"
    assert mock_typewrite.called, "pydirectinput.typewrite should be called"

    # Check that the real name was typed
    typewrite_calls = mock_typewrite.call_args_list
    found_real_name = False
    for call in typewrite_calls:
        if len(call[0]) > 0 and call[0][0] == "HUR-L1":
            found_real_name = True
            break

    assert found_real_name, f"typewrite should be called with real name 'HUR-L1', but got calls: {typewrite_calls}"


# --- Acceptance Criterion 2: Returns HTTP 400 for unknown alias ---

def test_trq011_returns_400_for_unknown_alias():
    """When destination alias is not found in YAML, endpoint must return HTTP 400 with 'Unknown destination: <alias>' error."""
    app.state.resolution = {"width": 2560, "height": 1440}

    with patch("ferdi.main.pydirectinput.press"), \
         patch("ferdi.main.pydirectinput.moveTo"), \
         patch("ferdi.main.pydirectinput.click"), \
         patch("ferdi.main.pydirectinput.typewrite"), \
         patch("ferdi.main.time.sleep"), \
         patch("ferdi.main.yaml.safe_load") as mock_yaml:

        mock_yaml.return_value = {
            "starmap": {
                "search_field_x_pct": 0.25,
                "search_field_y_pct": 0.10,
                "key_open": "F2",
                "key_validate": "enter",
                "key_close": "F2",
                "key_quantum": "b"
            },
            "validator": {"type": "bypass"},
            "destinations": {
                "Hurston L1": "HUR-L1",
                "ArcCorp L1": "ARC-L1"
            }
        }

        # POST with non-existent alias "NonExistent"
        response = client.post("/quantum-route", json={"destination": "NonExistent"})

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Unknown destination: NonExistent"


# --- Acceptance Criterion 3: Passthrough case (alias equals real name) ---

def test_trq011_passthrough_when_alias_equals_real_name():
    """When alias and real name are identical, typewrite is called with that name (passthrough case)."""
    app.state.resolution = {"width": 2560, "height": 1440}

    mock_typewrite = MagicMock()

    with patch("ferdi.main.pydirectinput.press"), \
         patch("ferdi.main.pydirectinput.moveTo"), \
         patch("ferdi.main.pydirectinput.click"), \
         patch("ferdi.main.pydirectinput.typewrite", mock_typewrite), \
         patch("ferdi.main.time.sleep"), \
         patch("ferdi.main.yaml.safe_load") as mock_yaml:

        mock_yaml.return_value = {
            "starmap": {
                "search_field_x_pct": 0.25,
                "search_field_y_pct": 0.10,
                "key_open": "F2",
                "key_validate": "enter",
                "key_close": "F2",
                "key_quantum": "b"
            },
            "validator": {"type": "bypass"},
            "destinations": {
                "Hurston": "Hurston",
                "ArcCorp": "ArcCorp"
            }
        }

        # POST with alias "Hurston" which maps to "Hurston" (same value)
        response = client.post("/quantum-route", json={"destination": "Hurston"})

    assert response.status_code == 200

    # Verify typewrite was called with "Hurston"
    assert mock_typewrite.called, "pydirectinput.typewrite should be called"
    typewrite_calls = mock_typewrite.call_args_list
    found_passthrough = False
    for call in typewrite_calls:
        if len(call[0]) > 0 and call[0][0] == "Hurston":
            found_passthrough = True
            break

    assert found_passthrough, f"typewrite should be called with 'Hurston', but got calls: {typewrite_calls}"


# --- Acceptance Criterion 4: YAML file is loaded to resolve mapping ---

def test_trq011_yaml_file_loaded_for_destination_resolution():
    """YAML file must be loaded to resolve destination alias→real-name mapping."""
    app.state.resolution = {"width": 2560, "height": 1440}

    with patch("ferdi.main.pydirectinput.press"), \
         patch("ferdi.main.pydirectinput.moveTo"), \
         patch("ferdi.main.pydirectinput.click"), \
         patch("ferdi.main.pydirectinput.typewrite"), \
         patch("ferdi.main.time.sleep"), \
         patch("ferdi.main.yaml.safe_load") as mock_yaml:

        # Mock YAML with destination mappings
        mock_yaml.return_value = {
            "starmap": {
                "search_field_x_pct": 0.25,
                "search_field_y_pct": 0.10,
                "key_open": "F2",
                "key_validate": "enter",
                "key_close": "F2",
                "key_quantum": "b"
            },
            "validator": {"type": "bypass"},
            "destinations": {
                "Hurston L1": "HUR-L1",
                "Hurston L2": "HUR-L2",
                "ArcCorp L1": "ARC-L1"
            }
        }

        response = client.post("/quantum-route", json={"destination": "Hurston L1"})

    assert response.status_code == 200

    # Verify that yaml.safe_load was called to load the configuration
    assert mock_yaml.called, "yaml.safe_load should be called to load configuration"


# --- Additional validation test: Error message includes the unknown alias ---

def test_trq011_error_message_includes_requested_alias():
    """When alias is unknown, error message must include the requested alias in 'Unknown destination: <alias>' format."""
    app.state.resolution = {"width": 2560, "height": 1440}

    with patch("ferdi.main.pydirectinput.press"), \
         patch("ferdi.main.pydirectinput.moveTo"), \
         patch("ferdi.main.pydirectinput.click"), \
         patch("ferdi.main.pydirectinput.typewrite"), \
         patch("ferdi.main.time.sleep"), \
         patch("ferdi.main.yaml.safe_load") as mock_yaml:

        mock_yaml.return_value = {
            "starmap": {
                "search_field_x_pct": 0.25,
                "search_field_y_pct": 0.10,
                "key_open": "F2",
                "key_validate": "enter",
                "key_close": "F2",
                "key_quantum": "b"
            },
            "validator": {"type": "bypass"},
            "destinations": {
                "Hurston L1": "HUR-L1"
            }
        }

        response = client.post("/quantum-route", json={"destination": "UnknownDest"})

    assert response.status_code == 400
    data = response.json()
    # Error detail should contain "Unknown destination:" followed by the requested alias
    assert "Unknown destination: UnknownDest" in data["detail"], \
        f"Expected error detail to contain 'Unknown destination: UnknownDest', got: {data['detail']}"


# --- Integration test: Multiple aliases mapped correctly ---

def test_trq011_multiple_aliases_resolved_correctly():
    """Multiple aliases should resolve to their corresponding real names."""
    app.state.resolution = {"width": 2560, "height": 1440}

    # Test with various alias/real-name combinations
    test_cases = [
        ("Hurston L1", "HUR-L1"),
        ("ArcCorp", "ArcCorp"),
        ("Area 18", "Area18"),
    ]

    for alias, expected_real_name in test_cases:
        mock_typewrite = MagicMock()

        with patch("ferdi.main.pydirectinput.press"), \
             patch("ferdi.main.pydirectinput.moveTo"), \
             patch("ferdi.main.pydirectinput.click"), \
             patch("ferdi.main.pydirectinput.typewrite", mock_typewrite), \
             patch("ferdi.main.time.sleep"), \
             patch("ferdi.main.yaml.safe_load") as mock_yaml:

            mock_yaml.return_value = {
                "starmap": {
                    "search_field_x_pct": 0.25,
                    "search_field_y_pct": 0.10,
                    "key_open": "F2",
                    "key_validate": "enter",
                    "key_close": "F2",
                    "key_quantum": "b"
                },
                "validator": {"type": "bypass"},
                "destinations": {
                    "Hurston L1": "HUR-L1",
                    "ArcCorp": "ArcCorp",
                    "Area 18": "Area18"
                }
            }

            response = client.post("/quantum-route", json={"destination": alias})

        assert response.status_code == 200, \
            f"Expected status 200 for alias '{alias}', got {response.status_code}"

        # Verify the correct real name was typed
        typewrite_calls = mock_typewrite.call_args_list
        found_real_name = any(
            len(call[0]) > 0 and call[0][0] == expected_real_name
            for call in typewrite_calls
        )
        assert found_real_name, \
            f"Expected typewrite to be called with '{expected_real_name}' for alias '{alias}', got: {typewrite_calls}"
