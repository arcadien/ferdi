# Project Notes

Operational lessons and tips for the ferdi project. Updated as we learn things.

## Testing

**Mock platform APIs in all tests** — Every test that exercises an endpoint backed by a platform-specific API (screen capture, audio, etc.) must mock that API, including simple existence/smoke tests. The Starlette TestClient re-raises unhandled app exceptions rather than returning HTTP 500, so an `OSError` from `PIL.ImageGrab.grab()` on a headless Linux CI runner crashes the test instead of returning a 500. Also wrap platform calls in the endpoint handler with try/except as a safety net.

**Mock multiple `yaml.safe_load` calls with `side_effect`** — When an endpoint loads more than one YAML file, test mocks must use `side_effect` with a list, not `return_value`. Using `return_value` injects the same dict into every call and can mask bugs where a file is never actually read.

```python
# Correct
mock_yaml.side_effect = [
    {"starmap": ..., "validator": ...},  # sc-config.yaml
    {"Hurston L1": "HUR-L1", ...},       # qt-destinations.yaml
]
```

**Use the `/test` skill** — Always invoke the `test` skill (via `Skill("test")`) when running the test suite; never call `uv run pytest` directly. It gives a compact, consistent output format.

## Environment

**Stop the server before `uv sync`** — When `uv run serve` is running, it holds locks on venv files. Running `uv sync` or recreating `.venv` while the server is active fails with "not a valid Python environment" errors. Stop the server first. If `.venv` is corrupt after a failed sync, delete it and re-run `uv sync --extra dev`.

## VoiceAttack

**Inline C# assembly references** — In VoiceAttack's "Execute an Inline C# Function" dialog, assemblies like `System.Net.Http` must be added in the References section of the dialog UI — not via `#r` or `//reference` directives in the code itself. The user ran into CS1069 errors before discovering this.

## Documentation

**Fix all occurrences when correcting a stale reference** — When requirements-analyst fixes a stale file reference (e.g. `qt-destinations.txt` → `.yaml`), grep the entire `technical-specifications.md` for the old string before committing. A partial fix will be caught by the docs-reviewer on the next run, requiring an extra cycle.
