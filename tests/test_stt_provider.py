"""
Acceptance tests for TRQ-005 — STTProvider interface and StaticSTT implementation (SPEC-005).

These tests are written before the implementation exists and are expected to
fail (RED) until ferdi/stt/ is created.
"""

import ast
import inspect
import os
from pathlib import Path


def test_trq005_stt_provider_interface_exists():
    """STTProvider must be an abstract class with a listen() method importable from ferdi.stt.base."""
    from ferdi.stt.base import STTProvider  # noqa: PLC0415

    # Must be an abstract class (has at least one abstract method)
    assert inspect.isabstract(STTProvider), "STTProvider must be an abstract class"

    # Must declare a listen() method
    assert hasattr(STTProvider, "listen"), "STTProvider must declare a listen() method"

    # listen() must be abstract — concrete subclasses that omit it cannot be instantiated
    abstract_methods = getattr(STTProvider, "__abstractmethods__", frozenset())
    assert "listen" in abstract_methods, "STTProvider.listen must be an abstract method"


def test_trq005_static_stt_implements_provider():
    """StaticSTT must be a subclass of STTProvider and listen() must return the configured text."""
    from ferdi.stt.base import STTProvider  # noqa: PLC0415
    from ferdi.stt.static_stt import StaticSTT  # noqa: PLC0415

    instance = StaticSTT("raise shields")

    assert isinstance(instance, STTProvider), "StaticSTT must be an instance of STTProvider"
    assert instance.listen() == "raise shields", (
        "StaticSTT.listen() must return the string passed at construction"
    )

    # Calling listen() multiple times must always return the same string
    assert instance.listen() == "raise shields", "StaticSTT.listen() must be idempotent"


def test_trq005_engine_does_not_import_concrete_stt():
    """ferdi/main.py must exist, expose set_stt_provider, and not import any concrete STT class."""
    main_path = Path(__file__).parent.parent / "ferdi" / "main.py"

    # The engine file must exist before this architectural guard makes sense.
    assert main_path.exists(), (
        "ferdi/main.py does not exist — the engine must be created before this test can pass"
    )

    source = main_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    # set_stt_provider must be defined in main.py so the provider can be injected.
    defined_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "set_stt_provider" in defined_names, (
        "ferdi/main.py must define a set_stt_provider() function for provider injection"
    )

    # No concrete STT class may be imported directly — coupling must go through the interface.
    concrete_names = {"StaticSTT", "WhisperSTT", "WebAPISTT"}

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Collect all imported names and module paths
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imported = {alias.name for alias in node.names}
                assert not (concrete_names & imported), (
                    f"ferdi/main.py must not import concrete STT classes, "
                    f"but found import of {concrete_names & imported} from '{module}'"
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in concrete_names, (
                        f"ferdi/main.py must not import concrete STT class '{alias.name}'"
                    )


def test_trq005_factory_selects_static_provider_from_env(monkeypatch):
    """build_stt_provider() with STT_PROVIDER=static must return a StaticSTT instance."""
    monkeypatch.setenv("STT_PROVIDER", "static")
    monkeypatch.setenv("STT_STATIC_TEXT", "engage hyperdrive")

    from ferdi.stt.factory import build_stt_provider  # noqa: PLC0415
    from ferdi.stt.static_stt import StaticSTT  # noqa: PLC0415

    provider = build_stt_provider()

    assert isinstance(provider, StaticSTT), (
        "build_stt_provider() must return a StaticSTT when STT_PROVIDER=static"
    )
    assert provider.listen() == "engage hyperdrive", (
        "The returned StaticSTT must return the value of STT_STATIC_TEXT"
    )


def test_trq005_static_stt_triggers_processing_pipeline(monkeypatch):
    """Injecting StaticSTT into the engine must make the command reach the processing pipeline."""
    from starlette.testclient import TestClient  # noqa: PLC0415

    from ferdi.stt.static_stt import StaticSTT  # noqa: PLC0415
    from ferdi.main import app, set_stt_provider  # noqa: PLC0415

    provider = StaticSTT("raise shields")
    set_stt_provider(provider)

    client = TestClient(app)
    response = client.post("/command", json={"command": "raise shields"})

    assert response.status_code == 200
    data = response.json()
    # The engine must have processed the command — the received field must match
    assert data.get("received") == "raise shields", (
        "The action engine must process the command provided by StaticSTT"
    )
