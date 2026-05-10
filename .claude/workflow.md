# Development Workflow

Generic workflow for requirement-driven TDD projects. Imported by `CLAUDE.md`.

## Conventional Commits

All commit messages **must** follow the [Conventional Commits](https://www.conventionalcommits.org/) format, enforced by a `conventional-pre-commit` hook.

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
- `req`: Changes to `requirements/` or `technical-specifications.md` — **mandatory** for any commit touching those files

Install the hook with: `pre-commit install --hook-type commit-msg`

## Branch management

Local commits on `main` are allowed.  
**Pushing to `main` is forbidden.** All changes must be pushed on a feature branch and merged via pull request.

Branch naming:
- `feat/<req-id>-<short-description>` — new feature or requirement implementation
- `fix/<short-description>` — bug fix
- `chore/<short-description>` — tooling, dependencies, configuration

When the user asks to push and the current branch is `main`, git-manager must:
1. Create an appropriate feature branch from current state
2. Push the feature branch with `-u origin`
3. Report the branch name and suggest `gh pr create`

## Environment management

All Python commands use **uv**:

```bash
uv add <package>          # add a dependency
uv sync --extra dev       # install all dependencies including dev extras
uv run pytest tests/ -v   # run the test suite
uv run python <script>    # run a script
```

Never use `pip` or `python` directly.

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
        │   Phase 4: docs-reviewer → GREEN (mandatory before PR)
        ▼
   Status: Implemented or Refactored ← git-manager commits requirements/<type>.md + technical-specifications.md
```

### Rules

- **Discuss requirements in conversation before writing any files.** Only write to `requirements/` once the user has agreed on the content.
- **No code is written before a requirement reaches `Validated` status.**
- The user must explicitly approve a requirement before TDD begins.
- Tests are written before implementation (TDD). Tests must be RED before implementation starts.
- The full test suite must be GREEN before a requirement is marked `Implemented`.
- Refactor only happens after all tests are green; tests must stay green throughout.
- `requirements/` and `technical-specifications.md` must always be sufficient for another agent or developer to re-implement any feature from scratch.
- **Any change to an existing implemented feature (endpoint rename, response format, behaviour change) must update `requirements/` and `technical-specifications.md` first, before touching code or tests.** Treat it as a new mini-cycle: discuss → update docs → update tests → update code → docs-reviewer → PR.

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

**Phase 4 — Documentation review (mandatory before PR)**

Delegate to **docs-reviewer**. It reads all files in `requirements/` and `technical-specifications.md` and runs six consistency checks.
- GREEN → delegate to **git-manager** to create the PR.
- RED → surface the report to the user. For each issue, the user either:
  - **Fixes** it: delegate corrections to **requirements-analyst**, commit via **git-manager**, then re-run **docs-reviewer**.
  - **Waives** it: acknowledge explicitly; **git-manager** lists waived issues in the PR body.

git-manager must not create a PR until docs-reviewer returns GREEN or all issues are waived.

## Agent architecture

Six specialized sub-agents handle all work. The orchestrator (main Claude) coordinates them.

| Agent | Model | Writes to |
|-------|-------|-----------|
| `requirements-analyst` | Haiku | `requirements/`, `technical-specifications.md` |
| `test-writer` | Haiku | `tests/` only |
| `implementer` | Sonnet | production code only |
| `refactorer` | Sonnet | production code only |
| `test-runner` | Haiku | nothing (read + run only) |
| `docs-reviewer` | Haiku | nothing (read only) |
| `git-manager` | Haiku | git history only |

### requirements-analyst

**Tools:** Read, Write, Edit — no shell execution.

Responsibilities:
- Write and update the appropriate file in `requirements/` and `technical-specifications.md`
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
- Discover and run the full test suite with `uv run pytest -v`
- Report RED / GREEN status with structured output
- List each test with pass/fail and failure details

### git-manager

**Tools:** Bash, Read — no file writes outside git.

Responsibilities:
- Stage specific files and create conventional commits
- Push feature branches and create PRs via `gh` CLI
- Enforce the `req` type rule: any commit touching `requirements/` or `technical-specifications.md` must use `req` type
- Never push to `main` — always push to a feature branch

### docs-reviewer

**Tools:** Read, Grep, Glob — no shell execution, no file writes.

Responsibilities:
- Read all files in `requirements/` and `technical-specifications.md` in full
- Run six consistency checks (prefix classification, bidirectional REQ↔SPEC links, status consistency, cross-file references, checkbox format, orphan SPECs)
- Return GREEN (all checks pass) or RED (structured report listing each issue with location and suggested fix)
- Never modify any file

## Requirement types

| Type | Prefix | When to use |
|------|--------|-------------|
| `business` | BRQ-NNN | Stakeholder value, product goals, user-facing behaviour |
| `technical` | TRQ-NNN | Technical constraints, API integrations, architecture decisions |
| `nonfunctional` | NFR-NNN | Performance, security, reliability, maintainability, scalability |
| `ui` | UIR-NNN | User interactions, visual elements, UX flows |

Each prefix has its own independent counter. Technical specifications use SPEC-NNN (independent counter).

## Requirement statuses

| Status | Meaning |
|--------|---------|
| `Draft` | Created, pending user review |
| `Validated` | Approved by the user — TDD cycle may begin |
| `In Progress` | Tests written (RED), implementation underway |
| `Implemented` | All tests GREEN, no refactor done |
| `Refactored` | All tests GREEN after a refactor pass |
| `Cancelled` | Dropped |
