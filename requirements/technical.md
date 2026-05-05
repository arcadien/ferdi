# Technical Requirements

Technical requirements (TRQ-NNN) for the **ferdi** project.
Linked to technical specifications in `technical-specifications.md`.

---

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
The ferdi project uses git for version control and GitHub for hosting. Maintaining a consistent, machine-readable commit history is required to support automated changelog generation (TRQ-004). Commits that do not follow a structured format cannot be parsed by changelog tools. Additionally, all changes to `requirements/` and `technical-specifications.md` must be committed in isolation to keep requirement documents in a consistent, auditable state.

**Description:**
All commits in the ferdi repository must follow the Conventional Commits specification: `<type>[(<scope>)]: <description>` in English. Allowed types are `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `chore`, `req`. Scope is optional. The convention must be enforced both locally (pre-commit hook via the `pre-commit` framework with `conventional-pre-commit`) and in CI (GitHub Actions step). The convention must also be documented in `CLAUDE.md`.

Additionally, a custom local `commit-msg` hook rejects any commit that stages files in `requirements/` or `technical-specifications.md` unless the commit message type is `req`. All changes to these files must be committed in isolation using the `req` type and documented in `CLAUDE.md`.

**Acceptance criteria:**
- [ ] A `.pre-commit-config.yaml` file exists at the repository root and includes the `conventional-pre-commit` hook
- [ ] Running `pre-commit install --hook-type commit-msg` installs the commit-msg hook locally
- [ ] A commit that does not follow the Conventional Commits format is rejected by the pre-commit hook with a clear error message
- [ ] A commit that follows the format is accepted by the hook
- [ ] The CI workflow (`.github/workflows/ci.yml`) includes a step that validates the commit message of the triggering commit using `conventional-pre-commit` or equivalent
- [ ] `CLAUDE.md` documents the Conventional Commits format as a mandatory convention for all commits
- [ ] The `pre-commit` package is listed in the project dev dependencies (`pyproject.toml`)
- [ ] `req` is listed as an allowed type in `.pre-commit-config.yaml` alongside `feat`, `fix`, etc.
- [ ] A custom local `commit-msg` hook rejects any commit that stages files in `requirements/` or `technical-specifications.md` unless the commit message type is `req`
- [ ] `CLAUDE.md` documents that all changes to `requirements/` and `technical-specifications.md` must be committed in isolation using the `req` type

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

### TRQ-005 — STTProvider interface and StaticSTT implementation

- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Spec:** SPEC-005

**Technical constraint:**
The action engine must not be coupled to any specific speech-to-text mechanism. Different deployment contexts (production, testing, debugging, external clients) require different input sources. The engine must operate identically regardless of how the text arrives.

**Description:**
Define an abstract `STTProvider` interface and a `StaticSTT` concrete implementation that returns a fixed configured string without audio. This is the foundation that all other STT providers build on.

**Acceptance criteria:**
- [ ] A `STTProvider` protocol/interface is defined
- [ ] `StaticSTT(text)` implements `STTProvider` and returns the configured text as the transcription
- [ ] The action engine imports only `STTProvider`, never a concrete implementation
- [ ] The active provider is selectable via configuration (e.g. environment variable or config file)
- [ ] `StaticSTT("raise shields")` triggers the same processing pipeline as a real voice command

### TRQ-006 — WhisperSTT implementation

- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Spec:** SPEC-006

**Technical constraint:**
Local speech-to-text transcription must work offline on a Windows PC without relying on cloud APIs.

**Description:**
A concrete `STTProvider` implementation that records audio from the microphone and transcribes it locally using faster-whisper.

**Acceptance criteria:**
- [ ] `WhisperSTT` implements `STTProvider`
- [ ] Model name is configurable (tiny, base, small, medium)
- [ ] An optional `initial_prompt` can be set via configuration to bias transcription toward Star Citizen vocabulary
- [ ] Recording duration or voice-activity detection boundary is configurable
- [ ] The provider works end-to-end: microphone input produces a transcribed string passed to the action engine

### TRQ-007 — WebAPISTT implementation

- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Spec:** SPEC-007

**Technical constraint:**
VoiceAttack and other external clients communicate with ferdi over HTTP. An STT provider that acts as an HTTP receiver enables these clients to inject text directly into the action engine.

**Description:**
A concrete `STTProvider` implementation that exposes an HTTP endpoint. External clients (e.g. VoiceAttack) POST text to this endpoint, which feeds it into the action engine.

**Acceptance criteria:**
- [ ] `WebAPISTT` implements `STTProvider`
- [ ] A POST `/stt` endpoint accepts a JSON body `{"text": "..."}` and passes the text to the action engine
- [ ] The endpoint returns a 200 response with the action engine result
- [ ] The port is configurable

### TRQ-008 — POST /detect-resolution endpoint

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-008

**Technical constraint:**
Screen resolution detection must be performed server-side on the ferdi backend so that Claude Vision or other vision-based processing pipelines can use the detected dimensions for screenshot analysis.

**Description:**
A FastAPI POST endpoint that detects the primary screen's resolution using a cross-platform library (screeninfo), stores it in application state for later use, and returns it with a confirmation message. The endpoint response is structured to allow clients (VoiceAttack or other frontends) to extract the resolution and provide vocal feedback to the user.

**Acceptance criteria:**
- [ ] A POST /detect-resolution endpoint exists
- [ ] The endpoint uses the `screeninfo` library to detect the primary monitor
- [ ] The detected resolution (width, height) is stored in `app.state.resolution`
- [ ] The endpoint returns HTTP 200 with `{"width": <int>, "height": <int>, "message": "<confirmation text>"}`
- [ ] If no primary monitor is found, the endpoint returns HTTP 500 with `{"detail": "No primary monitor found"}`

### TRQ-009 — POST /quantum-route endpoint

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-009

**Technical constraint:**
The quantum route flow is complex, involving multiple UI interactions, screen coordinate calculations based on resolution, and an extensible validator interface. A dedicated FastAPI endpoint must orchestrate these steps using configuration files (YAML for coordinates and keybindings) and a pluggable validator strategy.

**Description:**
A FastAPI POST endpoint that orchestrates the full quantum route flow. It accepts a destination name, uses the stored screen resolution to calculate UI element coordinates as percentages, loads UI configuration from `etc/sc-config.yaml`, executes mouse movements and key presses to open the star map, search for the destination, validate the route was set (using a pluggable validator), and activate quantum mode. The endpoint returns a confirmation message or an error if validation fails.

**Acceptance criteria:**
- [ ] A POST /quantum-route endpoint exists
- [ ] The endpoint accepts `{"destination": "<string>"}` as the request body
- [ ] The endpoint checks that `app.state.resolution` is set; returns HTTP 400 if not
- [ ] The endpoint loads UI configuration from `etc/sc-config.yaml`
- [ ] The endpoint calculates absolute UI coordinates from percentage values and resolution
- [ ] The endpoint opens the star map, searches for the destination, validates the result, and closes the star map
- [ ] The endpoint activates quantum mode by pressing the configured key
- [ ] The endpoint returns HTTP 200 with `{"destination": "...", "status": "ok", "message": "Quantum route to ... set"}`
- [ ] If the validator reports failure, the endpoint returns HTTP 500 with error detail

### TRQ-010 — Pluggable route validator interface

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-009

**Technical constraint:**
Route validation strategies may vary: for testing, a bypass validator is needed; for production, Claude Vision may validate by screenshot analysis. The validator must be pluggable to allow different implementations without changing the endpoint logic.

**Description:**
Define a `RouteValidator` abstract interface in `ferdi/validators/base.py` with a `validate(destination: str) -> bool` method. Provide two implementations: `BypassValidator` (always returns True) and `ClaudeVisionValidator` (stub for future enhancement). A factory function in `ferdi/validators/__init__.py` selects the active validator based on `etc/sc-config.yaml`.

**Acceptance criteria:**
- [ ] A `RouteValidator` abstract interface is defined with `validate(destination: str) -> bool`
- [ ] `BypassValidator` implements `RouteValidator` and always returns True
- [ ] `ClaudeVisionValidator` implements `RouteValidator` (stub implementation for now)
- [ ] A factory function selects the validator based on `validator.type` in the config
- [ ] Unknown validator types raise a `ValueError` with a descriptive message
- [ ] The validator is injected into the quantum-route endpoint (not imported directly)

### TRQ-011 — Destination alias-to-real-name mapping

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-010

**Technical constraint:**
Quantum travel destinations are stored with voice-friendly aliases that differ from their in-game names. VoiceAttack loads aliases for voice recognition, but the backend must look up real names and type them into the game's search bar for accuracy.

**Description:**
Quantum travel destinations are stored as alias→real-name pairs in `etc/qt-destinations.yaml`. VoiceAttack loads the alias keys for speech recognition at startup. The server receives the alias from the client, looks up the corresponding real name in the YAML file, and types the real name (not the alias) in the game's search bar. Unknown aliases are rejected with an HTTP 400 error.

**Acceptance criteria:**
- [ ] `etc/qt-destinations.yaml` exists with alias→real-name mappings
- [ ] The `POST /quantum-route` endpoint looks up the received destination alias in the YAML dict
- [ ] If the alias is found, the real name is typed in the search bar instead of the alias
- [ ] If the alias is not found, the endpoint returns HTTP 400 with `{ "detail": "Unknown destination: ..." }`
- [ ] VoiceAttack loads the alias keys from `etc/qt-destinations.yaml` at startup for the voice command list
- [ ] Both aliases and real names are stored consistently in a single YAML file
