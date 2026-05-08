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

---

## SPEC-003 — Conventional Commits Enforcement (TRQ-003)

- **Requirement:** TRQ-003
- **Date:** 2026-05-02
- **Status:** Implemented
- **Requirement type:** technical

### Overview

Conventional Commits is a standardized format for git commit messages that enables automated parsing, changelog generation, and semantic versioning. By enforcing this convention locally via pre-commit hooks and in CI via GitHub Actions, the ferdi project maintains a clean, machine-readable commit history that supports downstream automation and improves developer understanding of changes. The convention is enforced at the point of commit (local) and validated again in CI to ensure consistency. Additionally, a custom local `commit-msg` hook ensures that any commit staging changes to `requirements.md` or `technical-specifications.md` must use the `req` commit type, maintaining isolation and auditability of requirement changes.

### Architecture

```
Developer writes commit message
        │
        ▼
Pre-commit hook (conventional-pre-commit)
        │
        ├─ REJECTS non-compliant format (clear error)
        │
        └─ ACCEPTS compliant format
        │
        ▼
Commit pushed to GitHub
        │
        ▼
GitHub Actions CI workflow
        │
        └─ commitlint or conventional-pre-commit step
           validates commit message format
        │
        ├─ If valid → pass
        │
        └─ If invalid → fail workflow
        │
        ▼
Commit history remains clean and parseable
```

**Components:**
- `.pre-commit-config.yaml` — pre-commit framework configuration file
- `conventional-pre-commit` — hook implementation (pre-commit hook type)
- `pre-commit install --hook-type commit-msg` — local installation command
- `.github/workflows/ci.yml` — GitHub Actions workflow with commitlint step
- `pyproject.toml` — dev dependencies include `pre-commit`
- `CLAUDE.md` — documentation of the convention

**Conventional Commits format:**

```
<type>[(<scope>)]: <description>

[optional body]

[optional footer(s)]
```

**Allowed types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `chore`, `req`

**Examples:**
```
feat(voice-command): add support for multi-word voice commands
fix: correct FastAPI endpoint validation
docs: update README with installation instructions
ci: add commitlint to GitHub Actions workflow
req: refine TRQ-003 with requirements.md isolation requirement
```

### Custom Hook for Requirement Files

The `.pre-commit-config.yaml` includes a second custom local hook (type: `commit-msg`) that enforces isolation of requirement document changes. At commit time, this hook:

1. Runs `git diff --cached --name-only` to retrieve the list of staged files
2. Checks whether `requirements.md` or `technical-specifications.md` appear in the staged changeset
3. If either file is staged, it asserts that the commit message starts with `req:` (the `req` type)
4. If the assertion fails, it exits with a non-zero status and displays a clear error message:
   ```
   Error: Commits staging requirements.md or technical-specifications.md must use the 'req' type.
   Example: req: add new acceptance criterion to TRQ-003
   ```
5. If the check passes (or if no requirement files are staged), the hook exits cleanly

### Implementation Plan

1. Create `.pre-commit-config.yaml` at the repository root with:
   - Hook ID: `conventional-pre-commit`
   - Hook type: `commit-msg`
   - Configuration to reject non-compliant commit messages
2. Document the format and installation in `CLAUDE.md`:
   - Explain the Conventional Commits specification
   - Provide examples
   - Include the command `pre-commit install --hook-type commit-msg`
3. Add `pre-commit` to the dev dependencies in `pyproject.toml` (if not already present)
4. Update `.github/workflows/ci.yml` to include a step that validates commit messages using `commitlint` or `conventional-pre-commit`
5. Test locally by attempting to create a non-compliant commit (should be rejected) and a compliant commit (should be accepted)
6. Verify that the CI step correctly validates commit messages

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `.pre-commit-config.yaml` | Modify | Add `req` to allowed types list and implement custom `commit-msg` hook for requirement file isolation |
| `CLAUDE.md` | Modify | Add documentation of Conventional Commits convention and requirement file isolation requirement |
| `pyproject.toml` | Modify | Add `pre-commit` to dev dependencies (if needed) |
| `.github/workflows/ci.yml` | Modify | Add commitlint step to CI workflow |

### Testing

Acceptance criteria are verified through:

1. **Local hook installation** — Running `pre-commit install --hook-type commit-msg` succeeds and installs the commit-msg hook
2. **Non-compliant commit rejection** — Attempting to commit with message like "update code" is rejected with a clear error message
3. **Compliant commit acceptance** — A commit with message like "feat(api): add new endpoint" is accepted
4. **CI validation** — GitHub Actions workflow executes the commitlint or conventional-pre-commit step and:
   - Passes when the triggering commit message is compliant
   - Fails when the triggering commit message is non-compliant (catches edge cases where the local hook is bypassed)
5. **Documentation presence** — `CLAUDE.md` contains a "Commit message convention" or similar section explaining the format, allowed types, and examples

---

## SPEC-004 — On-Demand Release Workflow (TRQ-004)

- **Requirement:** TRQ-004
- **Date:** 2026-05-02
- **Status:** Implemented
- **Requirement type:** technical

### Overview

GitHub Actions `workflow_dispatch` enables manual triggering of workflows from the GitHub UI. For ferdi, an on-demand release workflow automates the creation of git tags and GitHub Releases without requiring manual CHANGELOG editing or commit operations. The workflow uses `git-cliff` to generate release notes directly from the project's conventional commit history (established by TRQ-003), groups commits by type (feat, fix, etc.), and publishes the generated notes exclusively in the GitHub Release body.

### Architecture

```
Maintainer triggers release workflow via GitHub UI
        │
        │  Provides version input (e.g. v1.0.0)
        │
        ▼
.github/workflows/release.yml (workflow_dispatch)
        │
        ├─ Checkout code
        ├─ Fetch git tags and history
        ├─ Install git-cliff
        │
        ▼
git-cliff (with cliff.toml config)
        │
        ├─ Parse commits since last tag
        ├─ Group by type (feat, fix, docs, etc.)
        ├─ Generate markdown release notes
        └─ Exclude non-user-facing types (chore, ci, style)
        │
        ▼
Create and push git tag (version input)
        │
        ▼
Publish GitHub Release
        │
        ├─ Tag: matches version input
        ├─ Body: git-cliff output
        └─ No CHANGELOG.md committed
        │
        ▼
Release published on GitHub Releases page
```

**Components:**
- `.github/workflows/release.yml` — GitHub Actions workflow definition (YAML)
- `cliff.toml` — git-cliff configuration for conventional commit grouping
- `git-cliff` — tool to parse commits and generate release notes
- `gh` CLI or `softprops/action-gh-release` — publish GitHub Release

**Conventional Commit grouping in cliff.toml:**

```toml
[changelog]

[[changelog.sections]]
title = "Features"
commit_parsers = [{message = "^feat", group = "Features"}]

[[changelog.sections]]
title = "Bug Fixes"
commit_parsers = [{message = "^fix", group = "Bug Fixes"}]

[[changelog.sections]]
title = "Documentation"
commit_parsers = [{message = "^docs", group = "Documentation"}]

# Skip non-user-facing types
skip_footers = ["chore", "ci", "style", "refactor", "test"]
```

### Implementation Plan

1. Create `.github/workflows/release.yml` with:
   - **Trigger:** `workflow_dispatch`
   - **Input:** `version` (required string, e.g. `v1.0.0`)
   - **Steps:**
     1. Checkout code: `actions/checkout@v4` with full history
     2. Fetch all tags: `git fetch --tags`
     3. Install `git-cliff`: via `cargo` or pre-built binary
     4. Generate release notes: `git-cliff --output CHANGELOG_TEMP.md --config cliff.toml`
     5. Create git tag: `git tag <version input>`
     6. Push tag: `git push origin <version input>`
     7. Publish release: Use `gh release create` or `softprops/action-gh-release@v1` with the generated notes
2. Create `cliff.toml` at repository root with conventional commit grouping configuration
3. Verify workflow syntax and test manually via GitHub Actions UI
4. Confirm release is published with correct tag and notes

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `.github/workflows/release.yml` | Create | GitHub Actions workflow for on-demand release with workflow_dispatch trigger |
| `cliff.toml` | Create | git-cliff configuration for conventional commit parsing and grouping |

### Testing

Acceptance criteria are verified through:

1. **Workflow syntax validation** — The YAML file must be valid GitHub Actions syntax
2. **Manual workflow trigger** — The workflow can be triggered via GitHub Actions UI with a version input
3. **Git tag creation** — After successful run, `git tag` lists the newly created tag
4. **GitHub Release publication** — A new release appears on the GitHub Releases page with:
   - Correct tag name (matches version input)
   - Release notes containing grouped commits (Features, Bug Fixes, Documentation, etc.)
   - No CHANGELOG.md in the commit history
5. **Commit grouping** — Release notes correctly:
   - Group commits by type (feat → Features, fix → Bug Fixes, etc.)
   - Include only user-facing types
   - Exclude chore, ci, style, refactor, test commits
6. **Configuration file validation** — `cliff.toml` is valid TOML and is used by git-cliff during execution

---

## SPEC-005 — STTProvider interface and StaticSTT implementation (TRQ-005)

- **Requirement:** TRQ-005
- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Requirement type:** technical

### Overview

The ferdi action engine must be decoupled from any concrete speech-to-text mechanism. This is achieved by defining an abstract `STTProvider` interface that all provider implementations must satisfy. A `StaticSTT` concrete implementation provides a deterministic, side-effect-free provider that returns a fixed string — used for automated tests, CI pipelines, and debug sessions. A factory function reads configuration at startup and injects the correct provider into the engine.

### Architecture

```
Configuration (env var / config file)
        │
        │  STT_PROVIDER=static | whisper | webapi
        │
        ▼
┌─────────────────────────┐
│  Provider Factory       │
│  build_stt_provider()   │
└─────────────────────────┘
        │
        │  returns an STTProvider instance
        │
        ▼
┌─────────────────────────────────────────────────┐
│  Action Engine                                  │
│  depends only on STTProvider (abstract)         │
│                                                 │
│  provider.listen() → str                        │
│  → processing pipeline                          │
└─────────────────────────────────────────────────┘
        ▲
        │
┌────────────────┐
│StaticSTT       │
│(fixed string)  │
└────────────────┘
```

**Components:**

| Component | Location | Purpose |
|-----------|----------|---------|
| `STTProvider` | `ferdi/stt/base.py` | Abstract base class / protocol defining the interface |
| `StaticSTT` | `ferdi/stt/static_stt.py` | Returns a fixed configured string; no audio |
| `build_stt_provider()` | `ferdi/stt/factory.py` | Reads configuration and returns the correct provider |

### Interface Contract

```python
# ferdi/stt/base.py
from abc import ABC, abstractmethod

class STTProvider(ABC):
    @abstractmethod
    def listen(self) -> str:
        """Block until a voice command is available and return it as text."""
        ...
```

All concrete implementations must subclass `STTProvider` and implement `listen() -> str`.

### Provider Specification — `StaticSTT`

- Constructor: `StaticSTT(text: str)`
- `listen()` always returns the string passed at construction
- No audio device, network, or filesystem access

### Configuration Entry Point

The factory function reads `STT_PROVIDER` from the environment (or a config file) and returns the appropriate instance:

| `STT_PROVIDER` value | Provider instantiated |
|----------------------|-----------------------|
| `static` | `StaticSTT` with text from `STT_STATIC_TEXT` env var |
| `whisper` | `WhisperSTT` (see SPEC-006) |
| `webapi` | `WebAPISTT` (see SPEC-007) |

Unknown values raise a `ValueError` with a descriptive message.

### Implementation Plan

1. Create `ferdi/stt/` package with `__init__.py`.
2. Create `ferdi/stt/base.py`: define `STTProvider` abstract base class with `listen() -> str`.
3. Create `ferdi/stt/static_stt.py`: implement `StaticSTT(text: str)`.
4. Create `ferdi/stt/factory.py`: implement `build_stt_provider()` reading `STT_PROVIDER` from environment; support `static` for now, delegate `whisper` and `webapi` to future specs.
5. Update the action engine (or `ferdi/main.py`) to accept an `STTProvider` instance via dependency injection rather than importing any concrete class.
6. Write tests covering all acceptance criteria.

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `ferdi/stt/__init__.py` | Create | Package marker |
| `ferdi/stt/base.py` | Create | `STTProvider` abstract interface |
| `ferdi/stt/static_stt.py` | Create | `StaticSTT` implementation |
| `ferdi/stt/factory.py` | Create | `build_stt_provider()` factory |
| `ferdi/main.py` | Modify | Inject `STTProvider` via dependency injection |
| `tests/test_stt_provider.py` | Create | Acceptance tests for TRQ-005 |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_stt_provider.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| `STTProvider` protocol/interface is defined | `test_trq005_stt_provider_interface_exists` | Import `STTProvider` from `ferdi.stt.base`; assert it is an abstract class with a `listen` method |
| `StaticSTT` implements `STTProvider` | `test_trq005_static_stt_implements_provider` | Assert `isinstance(StaticSTT("hi"), STTProvider)` and `StaticSTT("hi").listen() == "hi"` |
| Engine imports only the interface | `test_trq005_engine_does_not_import_concrete_stt` | Inspect `ferdi/main.py` source; assert no concrete STT class name appears in imports |
| Active provider selectable via config | `test_trq005_factory_selects_static_provider_from_env` | Set `STT_PROVIDER=static` and `STT_STATIC_TEXT=test`, call `build_stt_provider()`, assert returns a `StaticSTT` instance |
| `StaticSTT` triggers same pipeline | `test_trq005_static_stt_triggers_processing_pipeline` | Inject `StaticSTT("raise shields")` into the engine and assert the command reaches the processing pipeline |

---

## SPEC-006 — WhisperSTT implementation (TRQ-006)

- **Requirement:** TRQ-006
- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Requirement type:** technical

### Overview

`WhisperSTT` is a concrete `STTProvider` that records audio from the system microphone and transcribes it locally using the `faster-whisper` library. It runs entirely offline on Windows, requires no cloud API key, and integrates into the ferdi pipeline by returning a transcribed string to the action engine.

### Architecture

```
Microphone (default audio device)
        │
        │  raw audio frames (pyaudio / sounddevice)
        │
        ▼
┌─────────────────────────────┐
│  WhisperSTT.listen()        │
│  - record until VAD or      │
│    fixed duration elapses   │
│  - run faster-whisper       │
│    transcription            │
│  - return text string       │
└─────────────────────────────┘
        │
        ▼
Action Engine (STTProvider interface)
```

**Components:**

| Component | Location | Purpose |
|-----------|----------|---------|
| `WhisperSTT` | `ferdi/stt/whisper_stt.py` | Microphone recording + faster-whisper transcription |
| `faster-whisper` | PyPI dependency | Local Whisper model inference |
| `pyaudio` or `sounddevice` | PyPI dependency | Microphone audio capture |

### Provider Specification — `WhisperSTT`

- Constructor: `WhisperSTT(model: str = "base", initial_prompt: str | None = None, record_seconds: float = 5.0)`
- `model` selects the faster-whisper model size: `tiny`, `base`, `small`, or `medium`
- `initial_prompt` is an optional string passed to the faster-whisper `transcribe()` call to bias the model toward Star Citizen vocabulary (ship names, commands, etc.)
- `record_seconds` sets the maximum recording window; VAD may stop recording earlier if silence is detected
- `listen()` records audio, transcribes it, and returns the result string

### Configuration via Factory

When `STT_PROVIDER=whisper`, `build_stt_provider()` (SPEC-005) reads:

| Env var | Default | Purpose |
|---------|---------|---------|
| `WHISPER_MODEL` | `base` | Model size passed to `WhisperSTT` |
| `WHISPER_INITIAL_PROMPT` | _(none)_ | Optional transcription bias prompt |
| `WHISPER_RECORD_SECONDS` | `5.0` | Maximum recording window in seconds |

### Implementation Plan

1. Add `faster-whisper` and an audio capture library (`sounddevice` or `pyaudio`) to `pyproject.toml` dependencies.
2. Create `ferdi/stt/whisper_stt.py`: implement `WhisperSTT` subclassing `STTProvider`.
3. Implement `listen()`: capture audio for up to `record_seconds`, save to a temporary WAV file or in-memory buffer, run `faster_whisper.WhisperModel.transcribe()`, return the joined text segments.
4. Update `build_stt_provider()` in `ferdi/stt/factory.py` to handle `STT_PROVIDER=whisper`.
5. Write tests covering all acceptance criteria (use a pre-recorded WAV fixture to avoid hardware dependency in CI).

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `ferdi/stt/whisper_stt.py` | Create | `WhisperSTT` implementation |
| `ferdi/stt/factory.py` | Modify | Add `whisper` case to `build_stt_provider()` |
| `pyproject.toml` | Modify | Add `faster-whisper` and audio capture dependency |
| `tests/test_whisper_stt.py` | Create | Acceptance tests for TRQ-006 |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_whisper_stt.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| `WhisperSTT` implements `STTProvider` | `test_trq006_whisper_stt_implements_provider` | Assert `issubclass(WhisperSTT, STTProvider)` |
| Model name is configurable | `test_trq006_whisper_stt_model_configurable` | Instantiate `WhisperSTT(model="tiny")` and assert the stored model name equals `"tiny"` |
| `initial_prompt` is configurable | `test_trq006_whisper_stt_initial_prompt_configurable` | Instantiate with `initial_prompt="Star Citizen"` and assert it is stored |
| Recording boundary is configurable | `test_trq006_whisper_stt_record_seconds_configurable` | Instantiate with `record_seconds=3.0` and assert the stored value equals `3.0` |
| End-to-end transcription | `test_trq006_whisper_stt_end_to_end` | Feed a pre-recorded WAV fixture through `WhisperSTT.listen()` (mock mic input) and assert non-empty string returned |

---

## SPEC-007 — WebAPISTT implementation (TRQ-007)

- **Requirement:** TRQ-007
- **Date:** 2026-05-02
- **Status:** Implemented
- **Validated:** 2026-05-02
- **Requirement type:** technical

### Overview

`WebAPISTT` is a concrete `STTProvider` that exposes an HTTP POST endpoint. External clients such as VoiceAttack POST transcribed text to this endpoint, which passes the text directly into the ferdi action engine. The provider replaces the previous `POST /command` endpoint from TRQ-001 for STT-driven input, using a dedicated `/stt` route and returning the action engine result in the response body.

### Architecture

```
External client (e.g. VoiceAttack HTTP plugin)
        │
        │  POST http://127.0.0.1:<port>/stt
        │  Content-Type: application/json
        │  Body: {"text": "land at Port Olisar"}
        │
        ▼
┌─────────────────────────────────┐
│  WebAPISTT  (FastAPI sub-app    │
│  or mounted router)             │
│                                 │
│  POST /stt                      │
│  → extract "text" field         │
│  → pass to action engine        │
│  → return 200 + engine result   │
└─────────────────────────────────┘
        │
        ▼
Action Engine (STTProvider interface)
```

**Components:**

| Component | Location | Purpose |
|-----------|----------|---------|
| `WebAPISTT` | `ferdi/stt/webapi_stt.py` | HTTP endpoint + action engine bridge |
| FastAPI router | internal | Defines `POST /stt` route |

### Provider Specification — `WebAPISTT`

- Constructor: `WebAPISTT(port: int = 8000)`
- `port` is the TCP port the HTTP server listens on
- `listen()` blocks until a POST request is received on `/stt` and returns the `text` field from the request body
- The endpoint returns HTTP 200 with the action engine result as the response body
- A 422 response is returned when the request body is missing the `text` field

### Request and Response Contract

**Request — POST /stt**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | `string` | yes | Transcribed voice command text |

**Response — HTTP 200**

```json
{
  "status": "ok",
  "result": "<action engine output>"
}
```

**Error responses**

| Status | Trigger |
|--------|---------|
| 422 Unprocessable Entity | Missing or malformed JSON body |

### Configuration via Factory

When `STT_PROVIDER=webapi`, `build_stt_provider()` (SPEC-005) reads:

| Env var | Default | Purpose |
|---------|---------|---------|
| `WEBAPI_STT_PORT` | `8000` | TCP port for the HTTP server |

### Implementation Plan

1. Create `ferdi/stt/webapi_stt.py`: implement `WebAPISTT` subclassing `STTProvider`. Define a FastAPI router with `POST /stt`. The `listen()` method starts the server (or registers a handler) and returns received text.
2. Update `build_stt_provider()` in `ferdi/stt/factory.py` to handle `STT_PROVIDER=webapi`.
3. Write tests using FastAPI `TestClient` to cover all acceptance criteria without requiring a live HTTP server.

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `ferdi/stt/webapi_stt.py` | Create | `WebAPISTT` implementation |
| `ferdi/stt/factory.py` | Modify | Add `webapi` case to `build_stt_provider()` |
| `tests/test_webapi_stt.py` | Create | Acceptance tests for TRQ-007 |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_webapi_stt.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| `WebAPISTT` implements `STTProvider` | `test_trq007_webapi_stt_implements_provider` | Assert `issubclass(WebAPISTT, STTProvider)` |
| `POST /stt` accepts `{"text": "..."}` | `test_trq007_post_stt_accepts_text_body` | `TestClient.post("/stt", json={"text": "raise shields"})` → assert status 200 |
| Endpoint returns action engine result | `test_trq007_post_stt_returns_engine_result` | Assert response JSON contains `"status": "ok"` and a `"result"` key |
| Port is configurable | `test_trq007_webapi_stt_port_configurable` | Instantiate `WebAPISTT(port=9000)` and assert stored port equals `9000` |

---

## SPEC-008 — Detect Resolution Endpoint (BRQ-001, TRQ-008, NFR-001)

- **Requirements:** BRQ-001, TRQ-008, NFR-001
- **Date:** 2026-05-03
- **Status:** Implemented
- **Implemented:** 2026-05-03
- **Requirement type:** business, technical, non-functional

### Overview

The ferdi backend exposes a POST endpoint that detects the primary screen's resolution using a cross-platform library. The detected resolution is stored in application state for use by downstream processing (e.g., Claude Vision for screenshot analysis). Clients (VoiceAttack or other frontends) receive the detected dimensions and a confirmation message, which they can use to provide vocal feedback to the user.

### Architecture

```
Client (VoiceAttack or other frontend)
        │
        │  POST http://127.0.0.1:8000/detect-resolution
        │
        ▼
┌──────────────────────────────────┐
│  ferdi/main.py  (FastAPI)        │
│  POST /detect-resolution         │
│  → screeninfo.get_monitors()     │
│  → find primary monitor          │
│  → store in app.state.resolution │
│  → return 200 + resolution data  │
└──────────────────────────────────┘
        │
        │  HTTP 200
        │  {"width": 2560, "height": 1440, "message": "..."}
        │
        ▼
Client receives response
        │
        └─ Extract "message" → send to Say command
           (VoiceAttack or equivalent)
        │
        ▼
User hears vocal confirmation
```

**Components:**
- `screeninfo` library — cross-platform monitor detection
- `ferdi/main.py` — FastAPI POST /detect-resolution route
- `app.state.resolution` — application state storage for detected resolution

### Dependency Installation

Add `screeninfo` to the project dependencies:

```bash
uv add screeninfo
```

This library works on Windows, Linux (X11), and macOS by using platform-specific backend selection automatically.

### Endpoint Specification

**Request — POST /detect-resolution**

- No request body required
- HTTP method: POST

**Response — HTTP 200**

```json
{
  "width": 2560,
  "height": 1440,
  "message": "Resolution 2560 by 1440 detected"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `width` | `int` | Primary monitor width in pixels |
| `height` | `int` | Primary monitor height in pixels |
| `message` | `str` | Vocal confirmation message with detected dimensions |

**Error response — HTTP 500**

```json
{
  "detail": "No primary monitor found"
}
```

Returned when `screeninfo.get_monitors()` returns an empty list or no monitor has `is_primary == True`.

### Implementation Logic

1. Import `screeninfo` at module level
2. Define a Pydantic response model with fields `width`, `height`, `message`
3. Implement `POST /detect-resolution`:
   - Call `screeninfo.get_monitors()`
   - Filter for monitor where `is_primary == True`
   - If found:
     - Extract `width` and `height` attributes
     - Store `{"width": w, "height": h}` in `app.state.resolution`
     - Construct message: `f"Resolution {width} by {height} detected"`
     - Return HTTP 200 with response model
   - If not found:
     - Return HTTP 500 with `{"detail": "No primary monitor found"}`

### Client Integration (VoiceAttack example)

VoiceAttack's HTTP plugin can POST to `/detect-resolution` and extract the `message` field:

```
1. HTTP POST to http://127.0.0.1:8000/detect-resolution
2. Parse JSON response
3. Extract "message" field
4. Use "Say" command to speak the message to the user
```

Other frontends follow a similar pattern.

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Modify | Add `screeninfo` dependency |
| `ferdi/main.py` | Modify | Add POST /detect-resolution endpoint |
| `tests/test_detect_resolution.py` | Create | Acceptance tests for BRQ-001, TRQ-008, NFR-001 |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_detect_resolution.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| Endpoint exists and accepts POST | `test_brq001_detect_resolution_endpoint_exists` | `TestClient.post("/detect-resolution")` → assert status 200 or 500 |
| Detects primary monitor | `test_trq008_detects_primary_monitor` | Mock `screeninfo.get_monitors()` to return a primary monitor; POST → assert response width/height match mock data |
| Stores resolution in app.state | `test_trq008_stores_resolution_in_state` | POST to endpoint; assert `app.state.resolution` contains detected dimensions |
| Returns correct response format | `test_trq008_returns_correct_response_format` | Assert response JSON has `width`, `height`, `message` fields with correct types |
| Returns confirmation message | `test_brq001_returns_confirmation_message` | Assert `message` field contains the detected resolution (e.g., "2560 by 1440") |
| No primary monitor → HTTP 500 | `test_nfr001_no_monitor_returns_500` | Mock `screeninfo.get_monitors()` to return empty list; POST → assert status 500 and error detail |
| Cross-platform (Windows/Linux) | `test_nfr001_cross_platform_detection` | Assert `screeninfo` is used (no ctypes.windll or Xlib calls in implementation) |

---

## SPEC-009 — Quantum Route Endpoint (BRQ-002, TRQ-009, TRQ-010, NFR-002)

- **Requirements:** BRQ-002, TRQ-009, TRQ-010, NFR-002
- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Requirement type:** business, technical, non-functional

### Overview

The ferdi backend exposes a POST endpoint that orchestrates the full quantum route flow in Star Citizen. A voice command ("ferdi get a quantum route to [destination]") triggers the endpoint, which:
1. Verifies the screen resolution has been detected
2. Loads UI configuration and keybindings from a YAML file
3. Calculates UI element positions as percentages of screen resolution
4. Executes the sequence: open star map → search destination → validate route set → close star map → activate quantum
5. Returns a confirmation or error message

The endpoint uses a pluggable validator interface to support different validation strategies (bypass for testing, Claude Vision for production).

### Architecture

```
VoiceAttack voice command
        │
        │  "ferdi get a quantum route to Hurston"
        │
        ▼
┌────────────────────────────────────────┐
│  ferdi/main.py (FastAPI)               │
│  POST /quantum-route                   │
│  {"destination": "Hurston"}            │
└────────────────────────────────────────┘
        │
        ├─ Load app.state.resolution
        ├─ Load etc/sc-config.yaml
        ├─ Calculate absolute coordinates from percentages
        │
        ▼
┌────────────────────────────────────────┐
│  Quantum Route Orchestrator            │
│  1. Press key_open (F2)                │
│  2. Move mouse → click search field    │
│  3. Type destination                   │
│  4. Press key_validate (Enter)         │
│  5. Validate route set (pluggable)     │
│  6. Press key_close (F2)               │
│  7. Press key_quantum (B)              │
└────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│  Route Validator (pluggable)           │
│  • BypassValidator (always True)       │
│  • ClaudeVisionValidator (stub)        │
└────────────────────────────────────────┘
        │
        ▼
Response: {"destination": "...", "status": "ok", "message": "Quantum route to Hurston set"}
```

**Components:**

| Component | Location | Purpose |
|-----------|----------|---------|
| Quantum-route endpoint | `ferdi/main.py` | FastAPI POST /quantum-route handler |
| Route orchestrator | `ferdi/quantum_route.py` | Implements the full sequence of UI interactions |
| Route validator interface | `ferdi/validators/base.py` | Abstract `RouteValidator` interface |
| Bypass validator | `ferdi/validators/bypass.py` | Test implementation (always returns True) |
| Claude Vision validator | `ferdi/validators/claude_vision.py` | Production implementation (stub for now) |
| Validator factory | `ferdi/validators/__init__.py` | Selects active validator from config |
| UI destinations list | `etc/qt-destinations.yaml` | Alias→real-name mappings (see SPEC-010) |
| Configuration file | `etc/sc-config.yaml` | UI coordinates, keybindings, validator type |

### Configuration Files

#### `etc/qt-destinations.yaml`

YAML dictionary mapping aliases to real destination names. Used by VoiceAttack to build the spoken command list and by ferdi to look up the actual in-game names.

```yaml
Hurston: Hurston
Arccorp: Arccorp
Microtech: Microtech
Stanton: Stanton
Port Olisar: Port Olisar
Levski: Levski
```

#### `etc/sc-config.yaml`

Defines UI element positions as percentages, keybindings, and validator selection.

```yaml
starmap:
  search_field_x_pct: 0.25    # 25% from left edge
  search_field_y_pct: 0.10    # 10% from top edge
  key_open: F2                # Key to open/close star map
  key_validate: enter         # Key to confirm search
  key_close: F2               # Key to close star map
  key_quantum: b              # Key to activate quantum mode

validator:
  type: bypass                # bypass | claude-vision
```

### Endpoint Specification

**Request — POST /quantum-route**

```json
{
  "destination": "Hurston"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `destination` | `string` | yes | Star Citizen location name |

**Response — HTTP 200**

```json
{
  "destination": "Hurston",
  "status": "ok",
  "message": "Quantum route to Hurston set"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `destination` | `string` | Echo of the requested destination |
| `status` | `string` | Always `"ok"` on success |
| `message` | `string` | Confirmation message for vocal feedback |

**Error response — HTTP 400**

Returned when `app.state.resolution` has not been set.

```json
{
  "detail": "Resolution not detected. Run detect-resolution first."
}
```

**Error response — HTTP 500**

Returned when the validator reports failure.

```json
{
  "detail": "Could not confirm quantum route to Hurston"
}
```

### Validator Interface

#### `ferdi/validators/base.py`

```python
from abc import ABC, abstractmethod

class RouteValidator(ABC):
    @abstractmethod
    def validate(self, destination: str) -> bool:
        """
        Verify that a quantum route was successfully set.
        
        Args:
            destination: The destination name that should have been set
            
        Returns:
            True if validation succeeds, False otherwise
        """
        ...
```

#### `ferdi/validators/bypass.py`

```python
from ferdi.validators.base import RouteValidator

class BypassValidator(RouteValidator):
    """Always returns True. Used for testing without Claude Vision."""
    
    def validate(self, destination: str) -> bool:
        return True
```

#### `ferdi/validators/claude_vision.py`

```python
from ferdi.validators.base import RouteValidator

class ClaudeVisionValidator(RouteValidator):
    """Stub for future implementation. Takes a screenshot and validates via Claude."""
    
    def validate(self, destination: str) -> bool:
        # TODO: Implement in future requirement
        # For now, return True as a placeholder
        return True
```

#### `ferdi/validators/__init__.py`

```python
from ferdi.validators.base import RouteValidator
from ferdi.validators.bypass import BypassValidator
from ferdi.validators.claude_vision import ClaudeVisionValidator

def get_validator(config: dict) -> RouteValidator:
    """
    Factory function to select the active validator based on configuration.
    
    Args:
        config: Configuration dict (from etc/sc-config.yaml)
        
    Returns:
        An instance of the selected RouteValidator
        
    Raises:
        ValueError: If validator type is not recognized
    """
    type_ = config.get("validator", {}).get("type", "bypass")
    if type_ == "bypass":
        return BypassValidator()
    if type_ == "claude-vision":
        return ClaudeVisionValidator()
    raise ValueError(f"Unknown validator type: {type_}")
```

### Coordinate Calculation

All UI element positions are expressed as percentages (0.0 to 1.0) in the configuration file. At runtime, the endpoint converts to absolute coordinates:

```python
# Given resolution (from app.state.resolution) and percentage from config
x_pct = config["starmap"]["search_field_x_pct"]      # e.g., 0.25
y_pct = config["starmap"]["search_field_y_pct"]      # e.g., 0.10
width = app.state.resolution["width"]                 # e.g., 2560
height = app.state.resolution["height"]               # e.g., 1440

# Calculate absolute coordinates
absolute_x = int(width * x_pct)      # 2560 * 0.25 = 640
absolute_y = int(height * y_pct)     # 1440 * 0.10 = 144
```

### Orchestration Flow

The endpoint executes the following sequence:

1. **Validation:** Check that `app.state.resolution` is set (HTTP 400 if not)
2. **Load configuration:** Read `etc/sc-config.yaml`
3. **Initialize validator:** Call `get_validator(config)` to get the active validator
4. **Open star map:** Press `config["starmap"]["key_open"]` (e.g., F2)
5. **Wait for UI:** Sleep 1 second to allow the UI to load
6. **Calculate coordinates:** Convert search field percentages to absolute screen coordinates
7. **Move mouse and click:** Position mouse at (absolute_x, absolute_y) and click
8. **Type destination:** Send the destination string character by character
9. **Confirm search:** Press `config["starmap"]["key_validate"]` (e.g., Enter)
10. **Validate route:** Call `validator.validate(destination)` and check the result
    - If True: continue to step 11
    - If False: return HTTP 500 with error detail
11. **Close star map:** Press `config["starmap"]["key_close"]` (e.g., F2)
12. **Activate quantum:** Press `config["starmap"]["key_quantum"]` (e.g., B)
13. **Return success:** HTTP 200 with confirmation message

### Dependencies

The endpoint requires the `pydirectinput` library for mouse movement and keyboard input:

```bash
uv add pydirectinput
```

### Implementation Plan

1. Create `ferdi/validators/` package with `__init__.py`, `base.py`, `bypass.py`, `claude_vision.py`.
2. Create `ferdi/quantum_route.py` with the orchestration logic.
3. Add the `POST /quantum-route` endpoint to `ferdi/main.py`.
4. Create `etc/sc-config.yaml` and `etc/qt-destinations.txt` with example content.
5. Update `pyproject.toml` to add `pydirectinput` and `pyyaml` dependencies.
6. Write acceptance tests in `tests/test_quantum_route.py`.

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `ferdi/validators/__init__.py` | Create | Validator package marker and factory function |
| `ferdi/validators/base.py` | Create | `RouteValidator` abstract interface |
| `ferdi/validators/bypass.py` | Create | `BypassValidator` implementation |
| `ferdi/validators/claude_vision.py` | Create | `ClaudeVisionValidator` stub implementation |
| `ferdi/quantum_route.py` | Create | Orchestration logic for quantum route flow |
| `ferdi/main.py` | Modify | Add POST /quantum-route endpoint |
| `etc/sc-config.yaml` | Create | Configuration file with UI coordinates and keybindings |
| `etc/qt-destinations.yaml` | Create | Alias→real-name mappings for quantum destinations |
| `pyproject.toml` | Modify | Add `pydirectinput` and `pyyaml` dependencies |
| `tests/test_quantum_route.py` | Create | Acceptance tests for BRQ-002, TRQ-009, TRQ-010, NFR-002 |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_quantum_route.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| POST /quantum-route endpoint exists | `test_brq002_quantum_route_endpoint_exists` | `TestClient.post("/quantum-route", json={"destination": "Hurston"})` → assert status 200 or 400 or 500 |
| Endpoint accepts destination JSON | `test_brq002_endpoint_accepts_destination` | POST with valid destination → assert status 200 |
| Endpoint checks resolution is set | `test_trq009_checks_resolution_set` | Clear `app.state.resolution`; POST → assert status 400 with "Resolution not detected" |
| Endpoint loads YAML config | `test_trq009_loads_yaml_config` | Mock file read; verify config is loaded (test via coordinate calculation) |
| Calculates absolute coordinates | `test_nfr002_calculates_absolute_coordinates` | Given resolution 2560x1440 and x_pct=0.25, verify absolute_x = 640 |
| Validates at multiple resolutions | `test_nfr002_coordinates_work_at_multiple_resolutions` | Test coordinate conversion at 1920x1080, 2560x1440, 3840x2160 |
| Validator interface exists | `test_trq010_validator_interface_exists` | Import `RouteValidator`; assert it has `validate` method |
| BypassValidator returns True | `test_trq010_bypass_validator_always_true` | Instantiate `BypassValidator(); assert validate("any") == True` |
| ClaudeVisionValidator is stubbed | `test_trq010_claude_vision_validator_stubbed` | Instantiate `ClaudeVisionValidator(); assert validate("any") == True` |
| Factory selects bypass validator | `test_trq010_factory_selects_bypass` | Call `get_validator({"validator": {"type": "bypass"}})`; assert returns `BypassValidator` instance |
| Factory selects Claude Vision validator | `test_trq010_factory_selects_claude_vision` | Call `get_validator({"validator": {"type": "claude-vision"}})`; assert returns `ClaudeVisionValidator` instance |
| Factory rejects unknown type | `test_trq010_factory_rejects_unknown_type` | Call `get_validator({"validator": {"type": "unknown"}})`; assert raises `ValueError` |
| Returns success message | `test_brq002_returns_success_message` | POST with mocked orchestration; assert response JSON has status "ok" and message field |
| Returns error on validator failure | `test_trq009_returns_error_on_validation_failure` | Mock validator to return False; POST → assert status 500 with error detail |

---

## SPEC-010 — Destination Alias Mapping (TRQ-011)

- **Requirement:** TRQ-011
- **Date:** 2026-05-03
- **Status:** Implemented
- **Requirement type:** technical

### Overview

Quantum travel destinations in Star Citizen have in-game names (real names) that may be difficult to pronounce or remember in voice commands. Aliases provide voice-friendly alternatives that are easier to speak. The `etc/qt-destinations.yaml` file maps each alias to its real in-game name. VoiceAttack loads the alias keys for voice recognition, while the ferdi server looks up and types the real names into the game's search bar.

### Architecture

```
VoiceAttack voice command
        │
        │  "ferdi get a quantum route to Hurston L1"
        │  (alias from yaml keys)
        │
        ▼
┌────────────────────────────────────────┐
│  ferdi/main.py (FastAPI)               │
│  POST /quantum-route                   │
│  {"destination": "Hurston L1"}         │
│  (alias received)                      │
└────────────────────────────────────────┘
        │
        ├─ Load etc/qt-destinations.yaml
        ├─ Look up "Hurston L1" in dict
        ├─ Find real name: "HUR-L1"
        │
        ▼
┌────────────────────────────────────────┐
│  Type real name in search bar          │
│  pydirectinput.typewrite("HUR-L1")     │
└────────────────────────────────────────┘
        │
        ▼
Search result shows correct destination
```

**Components:**

| Component | Location | Purpose |
|-----------|----------|---------|
| Destination mappings | `etc/qt-destinations.yaml` | YAML dict mapping aliases to real names |
| Quantum route endpoint | `ferdi/main.py` | Modified to look up alias → real name |
| VoiceAttack config | external | Loads alias keys for voice command list |

### File Format

`etc/qt-destinations.yaml` is a flat YAML dictionary. Keys are voice-friendly aliases; values are in-game real names.

```yaml
# Hurston Lagrange points
Hurston L1: HUR-L1
Hurston L2: HUR-L2
Hurston L3: HUR-L3
Hurston L4: HUR-L4
Hurston L5: HUR-L5

# ArcCorp Lagrange points
ArcCorp L1: ARC-L1
ArcCorp L2: ARC-L2
ArcCorp L3: ARC-L3
ArcCorp L4: ARC-L4
ArcCorp L5: ARC-L5

# Crusader Lagrange points
Crusader L1: CRU-L1
Crusader L2: CRU-L2
Crusader L3: CRU-L3
Crusader L4: CRU-L4
Crusader L5: CRU-L5

# MicroTech Lagrange points
MicroTech L1: MIC-L1
MicroTech L2: MIC-L2
MicroTech L3: MIC-L3
MicroTech L4: MIC-L4
MicroTech L5: MIC-L5

# Planets
Hurston: Hurston
ArcCorp: ArcCorp
Crusader: Crusader
MicroTech: MicroTech

# Hurston moons
Aberdeen: Aberdeen
Arial: Arial
Ita: Ita
Magda: Magda

# ArcCorp moons
Lyria: Lyria
Wala: Wala

# Crusader moons
Cellin: Cellin
Daymar: Daymar
Yela: Yela

# MicroTech moons
Calliope: Calliope
Clio: Clio
Euterpe: Euterpe

# Landing zones
Lorville: Lorville
Area 18: Area18
Orison: Orison
New Babbage: New Babbage

# Space stations
Everus Harbor: Everus Harbor
Baijini Point: Baijini Point
Port Tressler: Port Tressler
Grim HEX: GrimHEX
Covalex Hub Gundo: Covalex Hub Gundo
INS Jericho: INS Jericho

# Jump points
Pyro Gateway: Pyro Gateway
Magnus Gateway: Magnus Gateway
```

**Key observations:**
- Some aliases match their real names (e.g., `Hurston: Hurston`)
- Some differ for pronunciation or brevity (e.g., `Area 18: Area18`, `Grim HEX: GrimHEX`)
- Lagrange points use voice-friendly names (e.g., `Hurston L1`) mapped to in-game codes (e.g., `HUR-L1`)
- Space station names may have special characters or spacing that the search bar handles differently

### Endpoint Change

The `POST /quantum-route` endpoint must be modified to:

1. Load `etc/qt-destinations.yaml` as a dictionary
2. Accept `{"destination": "<alias>"}` in the request body
3. Look up the alias in the dictionary
4. **If found:** Type the **real name** (dictionary value) instead of the alias
5. **If not found:** Return HTTP 400 with `{ "detail": "Unknown destination: <alias>" }`

**Error response example:**

```json
{
  "detail": "Unknown destination: Pyro Jump Point"
}
```

### VoiceAttack Integration

VoiceAttack's voice command list must load from the YAML alias keys:

```
1. Load etc/qt-destinations.yaml
2. Extract all keys (aliases)
3. Build voice command list from aliases
4. When alias is spoken, POST to /quantum-route with that alias
5. Server looks up real name and types it
```

This allows VoiceAttack to recognize "Hurston L1" and send it to ferdi, which looks up and types "HUR-L1" in the game search bar.

### Implementation Plan

1. Create `etc/qt-destinations.yaml` with the alias→real-name mappings (above).
2. Modify `ferdi/main.py` and/or `ferdi/quantum_route.py` to:
   - Load the YAML file at startup or per-request
   - In the `POST /quantum-route` handler: look up the received alias
   - If found: pass the real name to the typing function (not the alias)
   - If not found: return HTTP 400 with error detail
3. Update `pyproject.toml` to ensure `pyyaml` is listed as a dependency (if not already).
4. Remove `etc/qt-destinations.txt` (replaced by YAML).
5. Write acceptance tests in `tests/test_destination_mapping.py`.

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `etc/qt-destinations.yaml` | Create | Alias→real-name mappings for all quantum destinations |
| `etc/qt-destinations.txt` | Delete | Replaced by YAML format |
| `ferdi/main.py` or `ferdi/quantum_route.py` | Modify | Look up alias → real name before typing |
| `pyproject.toml` | Verify | Ensure `pyyaml` is in dependencies |
| `tests/test_destination_mapping.py` | Create | Acceptance tests for TRQ-011 |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_destination_mapping.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| YAML file exists with mappings | `test_trq011_yaml_file_exists` | Load `etc/qt-destinations.yaml`; assert it is a dict with at least 50 entries |
| Alias→real-name mappings are correct | `test_trq011_alias_mappings_correct` | Load YAML; assert `mappings["Hurston L1"] == "HUR-L1"` and similar for other entries |
| Endpoint looks up alias | `test_trq011_endpoint_looks_up_alias` | POST `/quantum-route` with `{"destination": "Hurston L1"}`; assert orchestration receives real name "HUR-L1" (via mock) |
| Known alias returns success | `test_trq011_known_alias_returns_200` | POST with known alias; assert status 200 |
| Unknown alias returns 400 | `test_trq011_unknown_alias_returns_400` | POST with `{"destination": "NonExistent"}`; assert status 400 with `"Unknown destination: NonExistent"` |
| Error message includes alias | `test_trq011_error_message_includes_alias` | Unknown alias POST; assert error detail contains the requested alias |
| VoiceAttack can load aliases | `test_trq011_voice_attack_loads_aliases` | Extract all keys from YAML; assert at least 50 unique aliases available |
| Real names are typed (not aliases) | `test_trq011_types_real_name_not_alias` | Mock `pydirectinput.typewrite()`; POST with alias; assert `typewrite()` called with real name |

---

## SPEC-011 — Screen Snapshot Endpoint (BRQ-003)

- **Requirement:** BRQ-003
- **Date:** 2026-05-05
- **Status:** Implemented
- **Validated:** 2026-05-05
- **Implemented:** 2026-05-05
- **Requirement type:** business

### Overview

The ferdi backend exposes a POST endpoint that captures the full screen as a PNG image and saves it to a timestamped file in the `screenshots/` directory. The endpoint returns the relative path to the saved file, which can be used by clients for subsequent processing (e.g., Claude Vision analysis). The screen capture logic is implemented as a reusable function, decoupled from the HTTP handler, so it can be called by other features in the future without duplicating code.

### Architecture

```
Client (VoiceAttack or other frontend)
        │
        │  POST http://127.0.0.1:8000/snapshot
        │
        ▼
┌──────────────────────────────────┐
│  ferdi/main.py  (FastAPI)        │
│  POST /snapshot                  │
│  → call capture_screen()         │
│  → save to screenshots/          │
│  → return 200 + file path        │
└──────────────────────────────────┘
        │
        │  HTTP 200
        │  {"path": "screenshots/2026-05-05_14-30-22.png"}
        │
        ▼
Client receives response
        │
        └─ Extract path → use for Claude Vision
           or other downstream processing
```

**Components:**

| Component | Location | Purpose |
|-----------|----------|---------|
| Capture function | `ferdi/screenshot.py` | Reusable `capture_screen() -> Path` function |
| Snapshot endpoint | `ferdi/main.py` | FastAPI POST /snapshot route |
| Pillow (PIL) | PyPI dependency | Image capture via `ImageGrab.grab()` |

### Dependency Installation

Add `Pillow` to the project dependencies:

```bash
uv add Pillow
```

Pillow's `ImageGrab` module works on Windows, macOS, and Linux (with xlib).

### Endpoint Specification

**Request — POST /snapshot**

- No request body required
- HTTP method: POST

**Response — HTTP 200**

```json
{
  "path": "screenshots/2026-05-05_14-30-22.png"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `path` | `string` | Relative path to the saved screenshot file (relative to the project root) |

### Reusable Capture Function

**`ferdi/screenshot.py`**

```python
from pathlib import Path
from datetime import datetime
from PIL import ImageGrab

def capture_screen() -> Path:
    """
    Capture the full screen and save as a PNG with a timestamp filename.
    
    Creates the screenshots/ directory if it does not exist.
    
    Returns:
        Path object pointing to the saved screenshot file (relative path)
    """
    # Create directory if needed
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Generate filename with current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}.png"
    file_path = screenshots_dir / filename
    
    # Capture screen and save
    image = ImageGrab.grab()
    image.save(file_path)
    
    return file_path
```

### Endpoint Implementation

In `ferdi/main.py`, define a response model and the POST route:

```python
from pydantic import BaseModel
from ferdi.screenshot import capture_screen

class SnapshotResponse(BaseModel):
    path: str

@app.post("/snapshot")
def take_snapshot() -> SnapshotResponse:
    """Capture the full screen and save to screenshots/ directory."""
    file_path = capture_screen()
    return SnapshotResponse(path=str(file_path))
```

### Files to Create or Modify

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Modify | Add `Pillow` dependency |
| `ferdi/screenshot.py` | Create | Reusable `capture_screen()` function |
| `ferdi/main.py` | Modify | Add POST /snapshot endpoint and `SnapshotResponse` model |
| `tests/test_snapshot.py` | Create | Acceptance tests for BRQ-003 |

### Testing

Each acceptance criterion maps to a pytest test in `tests/test_snapshot.py`:

| Criterion | Test name | Validation method |
|-----------|-----------|-------------------|
| Endpoint exists and accepts POST | `test_brq003_snapshot_endpoint_exists` | `TestClient.post("/snapshot")` → assert status 200 |
| Returns HTTP 200 with JSON body | `test_brq003_returns_200_with_json` | POST → assert status 200 and `response.headers["content-type"]` contains "application/json" |
| Response contains `path` field | `test_brq003_response_contains_path_field` | POST → assert `"path"` in `response.json()` |
| Path matches timestamp format | `test_brq003_path_matches_format` | POST → assert `response.json()["path"]` matches regex `screenshots/\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.png` |
| File exists on disk after call | `test_brq003_file_exists_on_disk` | POST → resolve returned path → assert `Path(path).exists()` |
| Screenshots directory created automatically | `test_brq003_screenshots_dir_created_automatically` | Delete `screenshots/` before POST → POST → assert `Path("screenshots").exists()` |
| Capture function is reusable | `test_brq003_capture_function_is_reusable` | Import `capture_screen` directly; call it; assert returned `Path` exists and is a PNG file |
| Timestamp format matches spec | `test_brq003_timestamp_format_correct` | POST → parse timestamp from path → assert it can be parsed with `strptime(..., "%Y-%m-%d_%H-%M-%S")` |
