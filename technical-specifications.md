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
- **Status:** Validated
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
