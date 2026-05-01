# ferdi — Claude Code Guide

Vocal agent for Star Citizen: VoiceAttack → FastAPI → Claude Vision → pydirectinput.

## Language rules

- All code, comments, and identifiers: **English**
- `requirements.md` and `technical-specifications.md`: **English**
- Conversation with the user: French or English, follow the user's language

## Development workflow

Every user request that adds or changes behaviour must be documented before implementation:

1. Run `/document <brief description of the request>` — this creates a REQ-NNN entry in
   `requirements.md` and a linked SPEC-NNN entry in `technical-specifications.md`.
2. Implement the feature according to the specification.
3. Run `/update-status REQ-NNN Implemented` once the feature is complete and tested.

The two documentation files must always be sufficient for another developer (or agent) to
re-implement the feature from scratch without reading the conversation history.

## Available custom commands

| Command | Purpose |
|---------|---------|
| `/document <request>` | Capture a requirement and write its technical specification |
| `/update-status REQ-NNN <status>` | Update requirement/spec status (`Draft`, `In Progress`, `Implemented`, `Cancelled`) |

## Repository layout

```
ferdi/
├── requirements.md              # All user requirements (REQ-NNN)
├── technical-specifications.md  # Technical specs linked to requirements (SPEC-NNN)
├── CLAUDE.md                    # This file
└── .claude/
    └── commands/                # Custom Claude Code slash commands
        ├── document.md
        └── update-status.md
```
