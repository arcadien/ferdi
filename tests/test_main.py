"""
Acceptance tests for TRQ-001 — FastAPI Skeleton (SPEC-001).

These tests are written before the implementation exists and are expected to
fail (RED) until ferdi/main.py is created.
"""

from starlette.testclient import TestClient

from ferdi.main import app  # noqa: E402 — will fail until implementation exists

client = TestClient(app)


def test_trq001_post_command_returns_200():
    """POST /command with a valid body must return HTTP 200."""
    response = client.post("/command", json={"command": "land at Port Olisar"})
    assert response.status_code == 200


def test_trq001_response_body_structure():
    """Response body must contain 'status' == 'ok' and 'received' == echoed command."""
    response = client.post("/command", json={"command": "test"})
    assert response.json() == {"status": "ok", "received": "test"}


def test_trq001_missing_body_returns_422():
    """POST /command with no body must return HTTP 422."""
    response = client.post("/command")
    assert response.status_code == 422


def test_trq001_malformed_body_returns_422():
    """POST /command with a body that is missing the 'command' field must return HTTP 422."""
    response = client.post("/command", json={"foo": "bar"})
    assert response.status_code == 422
