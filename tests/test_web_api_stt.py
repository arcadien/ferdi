"""
Acceptance tests for TRQ-007 — WebAPISTT implementation (SPEC-007).

These tests are written before the implementation exists and are expected to
fail (RED) until ferdi/stt/webapi_stt.py is created.
"""

import pytest


def test_trq007_webapi_stt_implements_provider():
    """WebAPISTT must be a subclass of STTProvider."""
    from ferdi.stt.base import STTProvider  # noqa: PLC0415
    from ferdi.stt.webapi_stt import WebAPISTT  # noqa: PLC0415

    assert issubclass(WebAPISTT, STTProvider), (
        "WebAPISTT must be a subclass of STTProvider"
    )


def test_trq007_post_stt_accepts_text_body():
    """POST /stt must accept {"text": "..."} and return HTTP 200."""
    from starlette.testclient import TestClient  # noqa: PLC0415

    from ferdi.stt.webapi_stt import WebAPISTT  # noqa: PLC0415

    instance = WebAPISTT()
    client = TestClient(instance.app)

    response = client.post("/stt", json={"text": "raise shields"})

    assert response.status_code == 200, (
        f"POST /stt must return 200, got {response.status_code}"
    )


def test_trq007_post_stt_returns_engine_result():
    """POST /stt must return a JSON body containing 'status': 'ok' and a 'result' key."""
    from starlette.testclient import TestClient  # noqa: PLC0415

    from ferdi.stt.webapi_stt import WebAPISTT  # noqa: PLC0415

    instance = WebAPISTT()
    client = TestClient(instance.app)

    response = client.post("/stt", json={"text": "engage hyperdrive"})

    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok", (
        f"Response must contain 'status': 'ok', got: {data}"
    )
    assert "result" in data, (
        f"Response must contain a 'result' key, got: {data}"
    )


def test_trq007_post_stt_missing_text_returns_422():
    """POST /stt with a missing 'text' field must return HTTP 422."""
    from starlette.testclient import TestClient  # noqa: PLC0415

    from ferdi.stt.webapi_stt import WebAPISTT  # noqa: PLC0415

    instance = WebAPISTT()
    client = TestClient(instance.app)

    response = client.post("/stt", json={"wrong_field": "oops"})

    assert response.status_code == 422, (
        f"POST /stt with missing 'text' field must return 422, got {response.status_code}"
    )


def test_trq007_webapi_stt_port_configurable():
    """WebAPISTT must store the port passed at construction."""
    from ferdi.stt.webapi_stt import WebAPISTT  # noqa: PLC0415

    instance = WebAPISTT(port=9000)

    assert instance.port == 9000, (
        "WebAPISTT must expose the configured port as .port"
    )


def test_trq007_factory_selects_webapi_provider_from_env(monkeypatch):
    """build_stt_provider() with STT_PROVIDER=webapi must return a WebAPISTT instance."""
    monkeypatch.setenv("STT_PROVIDER", "webapi")

    from ferdi.stt.factory import build_stt_provider  # noqa: PLC0415
    from ferdi.stt.webapi_stt import WebAPISTT  # noqa: PLC0415

    provider = build_stt_provider()

    assert isinstance(provider, WebAPISTT), (
        "build_stt_provider() must return a WebAPISTT when STT_PROVIDER=webapi"
    )
