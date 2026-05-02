# ferdi — Claude Code Guide

Vocal agent for Star Citizen: VoiceAttack → FastAPI → Claude Vision → pydirectinput.

## Language rules

- All code, comments, and identifiers: **English**
- `requirements.md` and `technical-specifications.md`: **English**
- Conversation with the user: French or English, follow the user's language

## Development workflow

```
/document <type> <description>
        │
        ▼
   Status: Draft
   (user reviews requirement and spec)
        │
        ▼ /validate <REQ-ID>
   Status: Validated
        │
        ▼ /tdd <REQ-ID>   ← Phase 1: write tests → RED
   Status: In Progress    ← Phase 2: implement   → GREEN (all tests)
        │                 ← Phase 3: refactor     → GREEN (optional)
        ▼
   Status: Implemented
      or Refactored
```

### Rules

- **Requirements are discussed with the user in conversation before any files are written.** The `/document` command is only called once the user has agreed on the requirement content.
- **No code is written before a requirement reaches `Validated` status.**
- The user must explicitly run `/validate` to approve a requirement.
- Tests are written before implementation (TDD). Tests must be RED before implementation starts.
- The full test suite must be GREEN before a requirement is marked `Implemented`.
- Refactor only happens after all tests are green; tests must stay green throughout.
- `requirements.md` and `technical-specifications.md` must always be sufficient for another agent or developer to re-implement any feature from scratch.

## Agent architecture

Two specialized sub-agents handle all work. Commands orchestrate them.

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

## Available custom commands

| Command | Purpose |
|---------|---------|
| `/document <type> <description>` | Capture a typed requirement and write its technical specification |
| `/validate <REQ-ID>` | Mark a requirement as validated by the user (required before TDD) |
| `/tdd <REQ-ID>` | Run the full TDD cycle: write tests (RED) → implement (GREEN) → refactor (optional) |
| `/update-status <REQ-ID> <status>` | Manually override status |

## Repository layout

```
ferdi/
├── requirements.md              # All requirements grouped by type (BRQ / TRQ / NFR / UIR)
├── technical-specifications.md  # Technical specs linked to requirements (SPEC-NNN)
├── CLAUDE.md                    # This file
└── .claude/
    ├── agents/
    │   ├── requirements-analyst.md   # Reads/writes files, writes code
    │   └── test-runner.md            # Runs tests, reports RED/GREEN
    └── commands/
        ├── document.md
        ├── validate.md
        ├── tdd.md
        └── update-status.md
```
