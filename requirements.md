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

### TRQ-003 — Conventional Commits Enforcement

- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Spec:** SPEC-003

**Technical constraint:**
The ferdi project uses git for version control and GitHub for hosting. Maintaining a consistent, machine-readable commit history is required to support automated changelog generation (TRQ-004). Commits that do not follow a structured format cannot be parsed by changelog tools. Additionally, all changes to `requirements.md` and `technical-specifications.md` must be committed in isolation to keep requirement documents in a consistent, auditable state.

**Description:**
All commits in the ferdi repository must follow the Conventional Commits specification: `<type>[(<scope>)]: <description>` in English. Allowed types are `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `chore`, `req`. Scope is optional. The convention must be enforced both locally (pre-commit hook via the `pre-commit` framework with `conventional-pre-commit`) and in CI (GitHub Actions step). The convention must also be documented in `CLAUDE.md`.

Additionally, a custom local `commit-msg` hook rejects any commit that stages `requirements.md` or `technical-specifications.md` unless the commit message type is `req`. All changes to these files must be committed in isolation using the `req` type and documented in `CLAUDE.md`.

**Acceptance criteria:**
- [ ] A `.pre-commit-config.yaml` file exists at the repository root and includes the `conventional-pre-commit` hook
- [ ] Running `pre-commit install --hook-type commit-msg` installs the commit-msg hook locally
- [ ] A commit that does not follow the Conventional Commits format is rejected by the pre-commit hook with a clear error message
- [ ] A commit that follows the format is accepted by the hook
- [ ] The CI workflow (`.github/workflows/ci.yml`) includes a step that validates the commit message of the triggering commit using `conventional-pre-commit` or equivalent
- [ ] `CLAUDE.md` documents the Conventional Commits format as a mandatory convention for all commits
- [ ] The `pre-commit` package is listed in the project dev dependencies (`pyproject.toml`)
- [ ] `req` is listed as an allowed type in `.pre-commit-config.yaml` alongside `feat`, `fix`, etc.
- [ ] A custom local `commit-msg` hook in `.pre-commit-config.yaml` rejects any commit that stages `requirements.md` or `technical-specifications.md` unless the commit message type is `req`
- [ ] `CLAUDE.md` documents that all changes to `requirements.md` and `technical-specifications.md` must be committed in isolation using the `req` type

### TRQ-004 — On-Demand Release Workflow

- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Spec:** SPEC-004

**Technical constraint:**
The ferdi project uses Conventional Commits (TRQ-003) to maintain a structured git history. Releases are created manually by the maintainer on demand. An automated mechanism is needed to generate release notes from conventional commits, tag the repository, and publish a GitHub Release — without committing a CHANGELOG file to the repository.

**Description:**
A GitHub Actions workflow must be created at `.github/workflows/release.yml` with a `workflow_dispatch` trigger. The workflow accepts a required version input (e.g. `v1.0.0`). It uses `git-cliff` to generate release notes from conventional commits since the last git tag. It then creates and pushes a git tag for the specified version, and publishes a GitHub Release with the git-cliff-generated notes as the release body. No CHANGELOG.md is committed to the repository; release notes live exclusively in the GitHub Release.

A `cliff.toml` configuration file must be added at the repository root to configure git-cliff's output format (conventional commits grouping by type: feat, fix, etc.).

**Acceptance criteria:**
- [ ] A `.github/workflows/release.yml` file exists with a `workflow_dispatch` trigger and a required `version` input
- [ ] The workflow generates release notes using `git-cliff` from commits since the previous tag
- [ ] The workflow creates and pushes a git tag matching the provided version input
- [ ] The workflow publishes a GitHub Release using the `gh` CLI or `softprops/action-gh-release`, with the git-cliff output as the release body
- [ ] A `cliff.toml` file exists at the repository root and configures conventional commit grouping (feat → Features, fix → Bug Fixes, etc.)
- [ ] No `CHANGELOG.md` is committed to the repository
- [ ] The workflow can be triggered manually from the GitHub Actions UI with a version string input
- [ ] The generated release notes correctly group commits by type and exclude non-user-facing types (chore, ci, style)

### TRQ-005 — Pluggable STT Provider Interface

- **Date:** 2026-05-02
- **Status:** Draft
- **Spec:** SPEC-005

**Technical constraint:**
The action engine must not be coupled to any specific speech-to-text mechanism. Different deployment contexts (production, testing, debugging, external clients) require different input sources. The engine must operate identically regardless of how the text arrives.

**Description:**
The action engine receives text through an abstract `STTProvider` interface. Three concrete implementations must be provided:
- `WhisperSTT` — handles microphone recording and transcription using faster-whisper locally
- `WebAPISTT` — exposes an HTTP endpoint that receives text (from VoiceAttack or any external client)
- `StaticSTT` — returns a fixed configured string without audio (for automated tests and debug)

The active provider is selected via configuration (environment variable or config file). The engine imports and depends only on the interface, never on a concrete implementation.

**Acceptance criteria:**
- [ ] The action engine imports only the `STTProvider` interface, never a concrete implementation
- [ ] The active provider is selectable via configuration (environment variable or config file) without modifying engine code
- [ ] `StaticSTT("raise shields")` triggers the same processing pipeline as a real voice command
- [ ] Adding a new provider requires modifying only the configuration entry point, not the engine

## Non-Functional Requirements

<!-- NFR entries go here -->

## UI Requirements

<!-- UIR entries go here -->
