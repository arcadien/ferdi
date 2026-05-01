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

- **No code is written before a requirement reaches `Validated` status.**
- The user must explicitly run `/validate` to approve a requirement.
- Tests are written before implementation (TDD). Tests must be RED before implementation starts.
- The full test suite must be GREEN before a requirement is marked `Implemented`.
- Refactor only happens after all tests are green; tests must stay green throughout.
- `requirements.md` and `technical-specifications.md` must always be sufficient for another agent or developer to re-implement any feature from scratch.

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
    └── commands/
        ├── document.md
        ├── validate.md
        ├── tdd.md
        └── update-status.md
```
