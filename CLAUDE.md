# ferdi — Claude Code Guide

Vocal agent for Star Citizen: VoiceAttack → FastAPI → Claude Vision → pydirectinput.

## Language rules

- All code, comments, and identifiers: **English**
- `requirements.md` and `technical-specifications.md`: **English**
- Conversation with the user: French or English, follow the user's language

## Conventional Commits

All commit messages **must** follow the [Conventional Commits](https://www.conventionalcommits.org/) format. This is enforced by the `conventional-pre-commit` hook.

### Format

```
type(scope): description
```

### Allowed types

- `feat`: A new feature or capability
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without feature/bug changes
- `test`: Test additions or updates
- `ci`: CI/CD configuration changes
- `chore`: Build process, dependencies, tooling changes
- `req`: Changes to `requirements.md` or `technical-specifications.md` — **mandatory** for any commit touching those files

### Examples

Valid commit messages:
```
feat(voice-commands): add support for StarCitizen navigation
fix: resolve FastAPI startup timeout issue
docs: update API endpoint documentation
refactor(visionapi): simplify image preprocessing
test: add acceptance tests for TRQ-003
ci(github-actions): add commit message validation
chore: update dependencies
```

The pre-commit hook is automatically installed when running `pre-commit install --hook-type commit-msg`. Commits that do not follow this format will be rejected.

## Development workflow

```
User describes requirement in conversation
        │
        ▼
   Status: Draft     ← requirements-analyst writes files, git-manager commits
   (user reviews)
        │
        ▼ User approves
   Status: Validated ← requirements-analyst updates status, git-manager commits
        │
        ▼ User asks to implement
   Status: In Progress
        │   Phase 1: test-writer → RED  → git-manager commits test files
        │   Phase 2: implementer → GREEN → git-manager commits impl files
        │   Phase 3: refactorer  → GREEN (optional)
        ▼
   Status: Implemented or Refactored ← git-manager commits requirements.md + technical-specifications.md
```

## Environment management

All Python commands use **uv**:

```bash
uv add <package>          # add a dependency
uv sync --dev             # install all dependencies including dev
uv run pytest tests/ -v   # run the test suite
uv run python <script>    # run a script
```

Never use `pip` or `python` directly.

### Rules

- **Requirements are discussed with the user in conversation before any files are written.** The `/document` command is only called once the user has agreed on the requirement content.
- **No code is written before a requirement reaches `Validated` status.**
- The user must explicitly run `/validate` to approve a requirement.
- Tests are written before implementation (TDD). Tests must be RED before implementation starts.
- The full test suite must be GREEN before a requirement is marked `Implemented`.
- Refactor only happens after all tests are green; tests must stay green throughout.
- `requirements.md` and `technical-specifications.md` must always be sufficient for another agent or developer to re-implement any feature from scratch.

### TDD cycle

**Phase 1 — Write failing tests (RED)**

Delegate to **test-writer**. Delegate to **test-runner** to confirm all new tests fail. If any pass unexpectedly, delegate back to **test-writer** to fix before continuing. Commit test files via **git-manager**.

**Phase 2 — Implement (GREEN)**

Delegate to **implementer** (max 2 attempts). After each attempt, delegate to **test-runner**.
- GREEN → commit implementation via **git-manager**, close the requirement.
- RED after attempt 1 → delegate to **implementer** again (attempt 2).
- RED after attempt 2 → **STOP**. The implementer returns an `ESCALATE` report. Surface it to the user: which tests still fail, what was tried, hypothesis. Wait for the user to amend the requirement, the test contract, or provide implementation hints before resuming.

**Test file freeze:** once tests are confirmed RED, test files must not be modified during Phase 2 or Phase 3. The freeze lifts only if the orchestrator explicitly decides the test contract was wrong — in which case return to Phase 1 with updated inputs.

**Phase 3 — Refactor (optional, user must request)**

Delegate to **refactorer**. Delegate to **test-runner** to confirm still GREEN. If the refactorer returns an `ESCALATE` report (a change would require modifying tests), surface it to the user before proceeding. Commit via **git-manager**.

## Agent architecture

Six specialized sub-agents handle all work. The orchestrator (main Claude) coordinates them.

| Agent | Model | Writes to |
|-------|-------|-----------|
| `requirements-analyst` | Haiku | `requirements.md`, `technical-specifications.md` |
| `test-writer` | Haiku | `tests/` only |
| `implementer` | Sonnet | production code only |
| `refactorer` | Sonnet | production code only |
| `test-runner` | Haiku | nothing (read + run only) |
| `git-manager` | Haiku | git history only |

### requirements-analyst

**Tools:** Read, Write, Edit — no shell execution.

Responsibilities:
- Write and update `requirements.md` and `technical-specifications.md`
- Update requirement and spec statuses

### test-writer

**Tools:** Read, Write, Edit — no shell execution.

Responsibilities:
- Read a requirement and its linked spec
- Write one failing test per acceptance criterion in `tests/`
- Never touch implementation files

### implementer

**Tools:** Read, Write, Edit — no shell execution.

Responsibilities:
- Write minimum production code to make specified failing tests pass
- Never modify test files
- 2-attempt budget; on exhaustion returns an `ESCALATE` report to the orchestrator

### refactorer

**Tools:** Read, Write, Edit — no shell execution.

Responsibilities:
- Improve production code readability and structure without changing observable behaviour
- Never modify test files
- Returns an `ESCALATE` report if a refactor would require changing a test

### test-runner

**Tools:** Bash, Read — no file writes.

Responsibilities:
- Discover and run the full test suite
- Report RED / GREEN status with structured output
- List each test with pass/fail and failure details

### git-manager

**Tools:** Bash, Read — no file writes outside git.

Responsibilities:
- Stage specific files and create conventional commits
- Push branches and create PRs via `gh` CLI
- Enforce the `req:` type rule: any commit touching `requirements.md` or `technical-specifications.md` must use `req` type

## Requirement types

| Type | Prefix | When to use |
|------|--------|-------------|
| `business` | BRQ-NNN | Stakeholder value, product goals, user-facing behaviour |
| `technical` | TRQ-NNN | Technical constraints, API integrations, architecture decisions |
| `nonfunctional` | NFR-NNN | Performance, security, reliability, maintainability, scalability |
| `ui` | UIR-NNN | User interactions, visual elements, UX flows |

Each prefix has its own independent counter.

## Requirement statuses

| Status | Meaning |
|--------|---------|
| `Draft` | Created, pending user review |
| `Validated` | Approved by the user — TDD cycle may begin |
| `In Progress` | Tests written (RED), implementation underway |
| `Implemented` | All tests GREEN, no refactor done |
| `Refactored` | All tests GREEN after a refactor pass |
| `Cancelled` | Dropped |

## Repository layout

```
ferdi/
├── requirements.md              # All requirements grouped by type (BRQ / TRQ / NFR / UIR)
├── technical-specifications.md  # Technical specs linked to requirements (SPEC-NNN)
├── CLAUDE.md                    # This file
└── .claude/
    └── agents/
        ├── requirements-analyst.md   # Writes requirements.md and technical-specifications.md
        ├── test-writer.md            # Writes failing tests from specs (Haiku)
        ├── implementer.md            # Implements code to pass tests (Sonnet)
        ├── refactorer.md             # Refactors passing code (Sonnet)
        ├── test-runner.md            # Runs tests, reports RED/GREEN (Haiku)
        └── git-manager.md            # Handles git commits, pushes, PRs (Haiku)
```
