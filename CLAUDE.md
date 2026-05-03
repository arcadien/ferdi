# ferdi — Claude Code Guide

Vocal agent for Star Citizen: VoiceAttack → FastAPI → Claude Vision → pydirectinput.

## Language rules

- All code, comments, and identifiers: **English**
- `requirements.md` and `technical-specifications.md`: **English**
- Conversation with the user: French or English, follow the user's language

All commits follow the **Conventional Commits** format — see `.claude/workflow.md` for the full specification, allowed types, branch management rules, TDD cycle, and agent architecture.

@.claude/workflow.md

## Repository layout

```
ferdi/
├── requirements.md              # All requirements grouped by type (BRQ / TRQ / NFR / UIR)
├── technical-specifications.md  # Technical specs linked to requirements (SPEC-NNN)
├── CLAUDE.md                    # This file
└── .claude/
    ├── workflow.md               # Generic reusable workflow (imported above)
    └── agents/
        ├── requirements-analyst.md
        ├── test-writer.md
        ├── implementer.md
        ├── refactorer.md
        ├── test-runner.md
        └── git-manager.md
```
