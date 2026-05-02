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

Any commit that stages `requirements.md` or `technical-specifications.md` **must** use the `req` type. Those files must never appear in a commit of another type.

Install the hook locally with: `pre-commit install --hook-type commit-msg`

### Examples

```
feat(voice-commands): add support for StarCitizen navigation
fix: resolve FastAPI startup timeout issue
req(trq-003): mark implemented
test(trq-004): write acceptance tests
ci: add git-manager agent and wire git commits into workflow
```

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
        │   Phase 1: write tests → RED  → git-manager commits test files
        │   Phase 2: implement   → GREEN → git-manager commits impl files
        │   Phase 3: refactor    → GREEN (optional)
        ▼
   Status: Implemented or Refactored ← git-manager commits requirements.md + technical-specifications.md
```

### Rules

- **Discuss requirements in conversation before writing any files.** Only delegate to requirements-analyst once the user has agreed on the content.
- **No code is written before a requirement reaches `Validated` status.**
- The user must explicitly approve a requirement before TDD begins.
- Tests are written before implementation (TDD). Tests must be RED before implementation starts.
- The full test suite must be GREEN before a requirement is marked `Implemented`.
- Refactor only happens after all tests are green; tests must stay green throughout.
- `requirements.md` and `technical-specifications.md` must always be sufficient for another agent or developer to re-implement any feature from scratch.

### Documenting a requirement

When the user agrees to document a requirement:

1. Delegate to **requirements-analyst**:
   > Document a new requirement of type `<type>` for this description: `<description>`.
   > 1. Read `requirements.md` to find the next available ID for this type.
   > 2. Append the requirement entry under the correct section using the standard template.
   > 3. Read `technical-specifications.md` to find the next SPEC-NNN number.
   > 4. Append the linked technical specification.
   > 5. Return a summary with the assigned IDs.

2. Delegate to **git-manager**:
   > Stage `requirements.md` and `technical-specifications.md`, commit with message `req(<id>): document <title>`.

3. Tell the user the requirement is in **Draft** status and ask them to review `requirements.md` and `technical-specifications.md`.

### Validating a requirement

When the user approves a requirement:

1. Pre-condition: status must be `Draft`. If not, report current status and stop.

2. Delegate to **requirements-analyst**:
   > Mark `<REQ-ID>` as Validated: replace `**Status:** Draft` with `**Status:** Validated` and add `**Validated:** <today>`.

3. Delegate to **git-manager**:
   > Stage `requirements.md`, commit with message `req(<id>): validate <title>`.

4. Tell the user the requirement is **Validated** and TDD can begin.

### TDD cycle

When the user asks to implement a validated requirement:

**Pre-condition:** status must be `Validated` or `In Progress`. If `Draft`, ask the user to approve first. If `Implemented` or `Refactored`, tell the user it is already done.

#### Phase 1 — Write failing tests (RED)

1. Delegate to **requirements-analyst**:
   > Read `requirements.md` for `<REQ-ID>` and its linked SPEC in `technical-specifications.md`.
   > Write one failing test per acceptance criterion. Follow existing project test conventions. Test names must reference the requirement ID. Tests must fail with the current codebase — do not write implementation code. Update status to `In Progress` in both files. Return the list of test names and **exact file paths** of all files modified.

2. Delegate to **test-runner**:
   > Run the test suite. We expect the new tests to FAIL (RED). Flag any that pass unexpectedly.

   If any new test passes unexpectedly, delegate back to requirements-analyst to fix it before continuing.

3. Delegate to **git-manager**:
   > Stage only the test file(s) (do NOT stage `requirements.md` or `technical-specifications.md`). Commit with message `test(<id>): write acceptance tests`.

4. Report the results and ask the user to confirm before proceeding to implementation.

#### Phase 2 — Implement (GREEN)

1. Delegate to **requirements-analyst**:
   > Implement the minimum code to make the failing tests for `<REQ-ID>` pass. Do not add behaviour beyond what the tests require. Return the **exact file paths** of all files created or modified (excluding `requirements.md` and `technical-specifications.md`).

2. Delegate to **test-runner**:
   > Run the **full test suite**. All tests must pass (GREEN), including pre-existing ones.

   If any test is RED, delegate back to requirements-analyst to fix, then re-run. Repeat until GREEN.

3. Delegate to **git-manager**:
   > Stage only the implementation file(s) (do NOT stage test files, `requirements.md`, or `technical-specifications.md`). Commit with message `feat(<id>): implement <title>`.

4. Report the results and ask the user if they want a refactor phase.

#### Phase 3 — Refactor (optional)

Only if the user asks for it.

1. Delegate to **requirements-analyst**:
   > Refactor the code produced for `<REQ-ID>`: improve readability, remove duplication, simplify logic. Do not change observable behaviour. Do not modify test files. Return the **exact file paths** of all files modified.

2. Delegate to **test-runner**:
   > Run the full test suite. All tests must still be GREEN.

   If any test went RED, tell the user and delegate back to requirements-analyst to fix.

3. Delegate to **git-manager**:
   > Stage only the refactored implementation file(s). Commit with message `refactor(<id>): <brief description>`.

#### Closing

1. Delegate to **requirements-analyst**:
   > Update status in `requirements.md` and the linked SPEC: set `Implemented` (or `Refactored` if a refactor was done).

2. Delegate to **git-manager**:
   > Stage `requirements.md` and `technical-specifications.md`. Commit with message `req(<id>): mark implemented` (or `mark refactored`).

3. Report the final status to the user.

### Updating status manually

When the user wants to force a status change:

Valid transitions: Draft → Validated, Validated → In Progress, In Progress → Implemented, Implemented → Refactored, any → Cancelled. Warn if the transition is non-standard but allow it if the user confirms.

Delegate to **requirements-analyst**:
> Update the status of `<REQ-ID>` to `<new-status>` in `requirements.md` and in the linked SPEC in `technical-specifications.md`. Return: requirement ID, spec ID, old status, new status.

## Agent architecture

Three specialized sub-agents handle all work.

### requirements-analyst

**Tools:** Read, Write, Edit — no shell execution.

Responsibilities:
- Write and update `requirements.md` and `technical-specifications.md`
- Write test code (Phase 1 of TDD)
- Write implementation code (Phase 2 of TDD)
- Refactor code (Phase 3 of TDD)
- Update requirement and spec statuses

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
        ├── requirements-analyst.md   # Reads/writes files, writes code
        ├── test-runner.md            # Runs tests, reports RED/GREEN
        └── git-manager.md            # Handles git operations and commits
```
