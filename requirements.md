# Requirements

This file documents all user requests as formal requirements for the **ferdi** project.
Requirements are linked to technical specifications in `technical-specifications.md`.

| Command | Action |
|---------|--------|
| `/document <type> <description>` | Create a new requirement (status: Draft) |
| `/validate <REQ-ID>` | Approve a requirement (status: Validated) — required before TDD |
| `/tdd <REQ-ID>` | Start TDD cycle: RED → GREEN → optional refactor |

## Requirement types and ID prefixes

| Type | Prefix |
|------|--------|
| Business | BRQ-NNN |
| Technical | TRQ-NNN |
| Non-Functional | NFR-NNN |
| UI | UIR-NNN |

## Status lifecycle

`Draft` → `Validated` → `In Progress` → `Implemented` / `Refactored`

---

## Business Requirements

<!-- BRQ entries go here -->

## Technical Requirements

### TRQ-001 — FastAPI Skeleton

- **Date:** 2026-05-01
- **Status:** Implemented
- **Validated:** 2026-05-01
- **Spec:** SPEC-001

**Technical constraint:**
VoiceAttack (Windows desktop application) sends voice commands to the ferdi backend via its HTTP plugin. The backend must expose an HTTP API that VoiceAttack can reach on localhost.

**Description:**
A FastAPI application must be created as the entry point for the ferdi system. It must expose a POST endpoint that accepts a JSON body containing the transcribed voice command string and returns a JSON acknowledgement. The project must include a proper file layout and a dependency manifest so the server can be installed and started on a Windows PC with a single command.

**Acceptance criteria:**
- [ ] A `POST /command` endpoint exists and accepts `{"command": "<string>"}` as the request body
- [ ] The endpoint returns HTTP 200 with a JSON body containing at least `{"status": "ok", "received": "<command string>"}`
- [ ] The application starts with `uvicorn ferdi.main:app` on `http://127.0.0.1:8000`
- [ ] A `pyproject.toml` (or `requirements.txt`) lists all runtime dependencies including `fastapi` and `uvicorn`
- [ ] The project layout places source code under a `ferdi/` package with an `__init__.py` and a `main.py` entry point
- [ ] A 422 response is returned when the request body is missing or malformed

### TRQ-002 — GitHub Actions CI

- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Spec:** SPEC-002

**Technical constraint:**
The ferdi project is hosted on GitHub (arcadien/ferdi) with Python 3.11+ and pytest as the test framework. Continuous integration must automatically verify that all tests pass on every push and pull request to maintain code quality and prevent regressions.

**Description:**
A GitHub Actions workflow must be created to automatically run the pytest test suite on every push and pull request. The workflow will run on ubuntu-latest, set up Python 3.11, install project dependencies from pyproject.toml, and execute pytest with verbose output. The workflow ensures that only code passing all tests is merged into the repository.

**Acceptance criteria:**
- [ ] A GitHub Actions workflow file exists at `.github/workflows/ci.yml`
- [ ] The workflow is triggered on push and pull_request events to any branch
- [ ] The workflow runs on ubuntu-latest
- [ ] Python 3.11 is set up using actions/setup-python@v5
- [ ] Dependencies are installed via `pip install -e ".[dev]"` to respect pyproject.toml configuration
- [ ] The test suite is executed with `pytest tests/ -v`
- [ ] The workflow passes (green) on the current codebase
- [ ] Workflow success is visible in pull request checks and commit status

## Non-Functional Requirements

<!-- NFR entries go here -->

## UI Requirements

<!-- UIR entries go here -->
