# Technical Specifications

This file contains the technical specification for each requirement documented in `requirements.md`.
Each specification is assigned a unique ID (SPEC-NNN) and references its parent requirement (REQ-NNN).

Specifications are created via the `/document` command. Together with `requirements.md`, they provide
enough information to automate or reproduce any implementation independently.

---

## SPEC-001 — FastAPI Skeleton (TRQ-001)

- **Requirement:** TRQ-001
- **Date:** 2026-05-01
- **Status:** Implemented
- **Requirement type:** technical

### Overview

The ferdi backend is a FastAPI application running locally on a Windows PC. VoiceAttack uses its built-in HTTP plugin to forward transcribed voice commands as JSON POST requests to the ferdi server. The FastAPI skeleton establishes the project structure, the dependency manifest, and the single endpoint that serves as the entry point for the entire agentic pipeline (screenshot → Claude Vision → action → loop).

### Architecture

```
VoiceAttack HTTP plugin
        │
        │  POST http://127.0.0.1:8000/command
        │  Content-Type: application/json
        │  Body: {"command": "land at Port Olisar"}
        ▼
┌─────────────────────────────┐
│  ferdi/main.py  (FastAPI)   │
│  POST /command              │
│  → validates request body   │
│  → returns {"status":"ok"}  │
│  → (future) triggers loop   │
└─────────────────────────────┘
```

**Components:**
- `ferdi/` — Python package (source root)
- `ferdi/__init__.py` — package marker
- `ferdi/main.py` — FastAPI `app` instance and route definitions
- `pyproject.toml` — project metadata and runtime dependencies
- `tests/` — pytest test suite

**Request contract — POST /command**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | `string` | yes | Transcribed voice command text |

**Response contract (HTTP 200)**

```json
{
  "status": "ok",
  "received": "<echo of the command string>"
}
```

**Error responses**

| Status | Trigger |
|--------|---------|
| 422 Unprocessable Entity | Missing or malformed JSON body (FastAPI/Pydantic default) |

### Implementation Plan

1. Create `pyproject.toml` with project metadata and dependencies (`fastapi`, `uvicorn[standard]`, `pytest`, `httpx`).
2. Create `ferdi/__init__.py` (empty, package marker).
3. Create `ferdi/main.py`: define a Pydantic `CommandRequest` model with a `command: str` field; define `POST /command` returning `{"status": "ok", "received": request.command}`.
4. Create `tests/__init__.py` (empty).
5. Create `tests/test_main.py` with pytest tests using FastAPI's `TestClient`.
6. Verify the server starts with `uvicorn ferdi.main:app --host 127.0.0.1 --port 8000`.

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Create | Project metadata, runtime and dev dependencies |
| `ferdi/__init__.py` | Create | Marks `ferdi` as an importable Python package |
| `ferdi/main.py` | Create | FastAPI application and `POST /command` route |
| `tests/__init__.py` | Create | Marks `tests` as a package for pytest discovery |
| `tests/test_main.py` | Create | Acceptance tests for TRQ-001 criteria |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_main.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| `POST /command` accepts `{"command": "..."}` and returns 200 | `test_trq001_post_command_returns_200` | `TestClient.post("/command", json={"command": "test"})` → assert status 200 |
| Response body contains `status` and `received` | `test_trq001_response_body_structure` | Assert `response.json() == {"status": "ok", "received": "test"}` |
| Missing body returns 422 | `test_trq001_missing_body_returns_422` | `TestClient.post("/command")` with no body → assert status 422 |
| Malformed body (missing `command` field) returns 422 | `test_trq001_malformed_body_returns_422` | `TestClient.post("/command", json={"foo": "bar"})` → assert status 422 |

---

## SPEC-002 — GitHub Actions CI (TRQ-002)

- **Requirement:** TRQ-002
- **Date:** 2026-05-02
- **Status:** Implemented
- **Requirement type:** technical

### Overview

GitHub Actions provides a CI/CD platform integrated directly into GitHub repositories. For ferdi, a workflow automates the execution of the pytest test suite on every code change (push or pull request). This ensures that all commits maintain test coverage and prevents regressions from being merged. The workflow is lightweight, declarative, and requires no external CI infrastructure.

### Architecture

```
Developer pushes code to GitHub
        │
        ▼
GitHub detects push or pull_request event
        │
        ▼
Workflow trigger: .github/workflows/ci.yml
        │
        ├─ Set up ubuntu-latest runner
        ├─ Install Python 3.11
        ├─ Install dependencies: pip install -e ".[dev]"
        │
        ▼
pytest tests/ -v
        │
        ├─ If all tests pass → green check (✓)
        │
        └─ If any test fails → red check (✗)
        │
        ▼
Pull request checks / commit status updated
```

**Components:**
- `.github/workflows/ci.yml` — GitHub Actions workflow definition (YAML)
- `ubuntu-latest` runner — Linux environment with Python runtime
- `actions/setup-python@v5` — GitHub action to install specified Python version
- `pytest tests/ -v` — command to execute the full test suite

### Implementation Plan

1. Create directory `.github/workflows/` if it does not exist.
2. Create `.github/workflows/ci.yml` with the following structure:
   - **Name:** "CI"
   - **Trigger:** `on: [push, pull_request]`
   - **Jobs:** Single job named `test`
   - **Runs on:** `ubuntu-latest`
   - **Steps:**
     1. Check out code: `actions/checkout@v4`
     2. Set up Python 3.11: `actions/setup-python@v5` with `python-version: '3.11'`
     3. Install dependencies: `pip install -e ".[dev]"`
     4. Run tests: `pytest tests/ -v`
3. Verify workflow syntax and that the workflow executes successfully on the current codebase.
4. Confirm that workflow runs appear in pull request status checks and commit history.

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `.github/workflows/ci.yml` | Create | GitHub Actions workflow definition for CI |

### Testing

Workflow validation is verified by:

1. **Workflow syntax check** — The YAML file must be valid GitHub Actions syntax (GitHub will reject invalid files automatically).
2. **Successful execution on current codebase** — The workflow must complete with exit code 0 (all tests pass).
3. **Visibility in GitHub UI** — On a test pull request or commit push, workflow status must appear in:
   - Commit status checks
   - Pull request "Checks" tab
4. **Test command execution** — `pytest tests/ -v` must run and report results with verbose output.

The workflow itself is not unit-tested; its correctness is verified by observing:
- Successful runs on new commits
- Proper detection of test failures (workflow should fail if any test fails)
- Correct Python version and dependency installation from pyproject.toml
