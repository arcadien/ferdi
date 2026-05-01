# ferdi — Claude Code Guide

Vocal agent for Star Citizen: VoiceAttack → FastAPI → Claude Vision → pydirectinput.

## Language rules

- All code, comments, and identifiers: **English**
- `requirements.md` and `technical-specifications.md`: **English**
- Conversation with the user: French or English, follow the user's language

## Development workflow

Every user request that adds or changes behaviour must be documented before implementation:

1. Run `/document <type> <description>` — creates a typed requirement entry in `requirements.md`
   and a linked SPEC-NNN entry in `technical-specifications.md`.
2. Implement the feature according to the specification.
3. Run `/update-status <REQ-ID> Implemented` once the feature is complete and tested.

The two documentation files must always be sufficient for another developer (or agent) to
re-implement the feature from scratch without reading the conversation history.

## Requirement types

| Type | Prefix | When to use |
|------|--------|-------------|
| `business` | BRQ-NNN | Stakeholder value, product goals, user-facing behaviour |
| `technical` | TRQ-NNN | Technical constraints, API integrations, architecture decisions |
| `nonfunctional` | NFR-NNN | Performance, security, reliability, maintainability, scalability |
| `ui` | UIR-NNN | User interactions, visual elements, UX flows |

Each type counter is independent (BRQ-001, TRQ-001, NFR-001, UIR-001 can all coexist).

## Available custom commands

| Command | Purpose |
|---------|---------|
| `/document <type> <description>` | Capture a typed requirement and write its technical specification |
| `/update-status <REQ-ID> <status>` | Update status (`Draft`, `In Progress`, `Implemented`, `Cancelled`) |

## Repository layout

```
ferdi/
├── requirements.md              # All requirements, grouped by type (BRQ / TRQ / NFR / UIR)
├── technical-specifications.md  # Technical specs linked to requirements (SPEC-NNN)
├── CLAUDE.md                    # This file
└── .claude/
    └── commands/                # Custom Claude Code slash commands
        ├── document.md
        └── update-status.md
```
