# Requirements

This file documents all user requests as formal requirements for the **ferdi** project.
Requirements are linked to technical specifications in `technical-specifications.md`.

| Command | Action |
|---------|--------|
| `/document <type> <description>` | Create a new requirement (status: Draft) |
| `/validate <REQ-ID>` | Approve a requirement (status: Validated) — required before TDD |
| `/tdd <REQ-ID>` | Start TDD cycle: RED → GREEN → optional refactor |

## Requirement types and ID prefixes

| Type | Prefix |
|------|--------|
| Business | BRQ-NNN |
| Technical | TRQ-NNN |
| Non-Functional | NFR-NNN |
| UI | UIR-NNN |

## Status lifecycle

`Draft` → `Validated` → `In Progress` → `Implemented` / `Refactored`

---

## Business Requirements

### BRQ-001 — Requirement-driven development

- **Date:** 2026-05-01
- **Validated:** 2026-05-01
- **Status:** Implemented
- **Spec:** SPEC-001

**Description:**
Every user request must be captured as a formal requirement before any code is written. The two
documentation files (`requirements.md`, `technical-specifications.md`) must always be sufficient for
another developer or agent to re-implement any feature from scratch without reading the conversation
history.

**Business context:**
The ferdi project is built by Claude Code agents operating autonomously. Formal requirements ensure
that decisions are traceable, reproducible, and independent of any particular conversation session.

**Acceptance criteria:**
- Every feature or change starts with a documented requirement
- No implementation code is written before the requirement is Validated
- `requirements.md` and `technical-specifications.md` together fully describe each feature

---

## Technical Requirements

### TRQ-001 — Typed requirement management with independent ID counters

- **Date:** 2026-05-01
- **Validated:** 2026-05-01
- **Status:** Implemented
- **Spec:** SPEC-002

**Description:**
Requirements are classified into four types, each with its own ID prefix and independent numeric
counter: Business (BRQ-NNN), Technical (TRQ-NNN), Non-Functional (NFR-NNN), UI (UIR-NNN).

**Technical constraint:**
The ID scheme must allow the same numeric suffix to appear under different prefixes (e.g. BRQ-001
and TRQ-001 are distinct requirements). Counters must not be shared across types.

**Acceptance criteria:**
- Each type uses its own prefix
- Counters are independent (BRQ-001 and TRQ-001 can coexist)
- Each requirement entry includes: ID, date, status, description, acceptance criteria
- Template varies per type (business context / technical constraint / metric / user story)

---

### TRQ-002 — Technical specification linked to each requirement

- **Date:** 2026-05-01
- **Validated:** 2026-05-01
- **Status:** Implemented
- **Spec:** SPEC-003

**Description:**
Every requirement in `requirements.md` has a corresponding SPEC-NNN entry in
`technical-specifications.md`. The spec provides enough detail to implement the requirement without
reading the conversation.

**Technical constraint:**
The SPEC counter is independent of all requirement counters. A SPEC entry must be created atomically
with its parent requirement (same `/document` invocation).

**Acceptance criteria:**
- Each requirement maps to exactly one SPEC-NNN
- Spec includes: overview, architecture, implementation plan, files to create/modify, testing approach
- Spec status mirrors requirement status

---

### TRQ-003 — Claude Code custom commands for the development workflow

- **Date:** 2026-05-01
- **Validated:** 2026-05-01
- **Status:** Implemented
- **Spec:** SPEC-004

**Description:**
The development workflow is driven by four slash commands defined as markdown files in
`.claude/commands/`. Each command has a specific role in the requirement lifecycle and TDD cycle.

**Technical constraint:**
Commands must be markdown files readable by Claude Code. They must delegate to the correct
sub-agent (requirements-analyst or test-runner) and must not conflate responsibilities.

**Acceptance criteria:**
- All four commands exist as markdown files in `.claude/commands/`
- `/tdd` enforces the RED → GREEN order with explicit user confirmation checkpoints
- Commands delegate work to the appropriate sub-agent (requirements-analyst or test-runner)

---

### TRQ-004 — Two specialized sub-agents

- **Date:** 2026-05-01
- **Validated:** 2026-05-01
- **Status:** Implemented
- **Spec:** SPEC-005

**Description:**
Two Claude Code sub-agents defined in `.claude/agents/` handle all work. The requirements-analyst
agent reads, writes, and edits files but cannot execute shell commands. The test-runner agent runs
the test suite and reports results but cannot write files.

**Technical constraint:**
Tool restrictions are enforced by the agent definition files (`tools:` field). Neither agent may
exceed its declared tool set.

**Acceptance criteria:**
- requirements-analyst cannot execute shell commands
- test-runner cannot write or modify source files
- test-runner output is structured: status banner, per-test table, failure details, summary counts

---

## Non-Functional Requirements

### NFR-001 — TDD enforcement — tests before implementation

- **Date:** 2026-05-01
- **Validated:** 2026-05-01
- **Status:** Implemented
- **Category:** Maintainability
- **Spec:** SPEC-006

**Description:**
No implementation code may be written before failing tests exist for the corresponding requirement.
Tests must be RED before implementation starts. The full test suite must be GREEN before a
requirement is marked Implemented.

**Target metric:** 0 requirements marked Implemented without a prior RED test run recorded.

**Acceptance criteria:**
- `/tdd` writes tests before any implementation code
- `/tdd` pauses and requires user confirmation that tests are RED before proceeding
- `/tdd` runs the full suite (not just new tests) to confirm GREEN
- Refactor phase only starts after full GREEN suite

---

### NFR-002 — Language consistency

- **Date:** 2026-05-01
- **Validated:** 2026-05-01
- **Status:** Implemented
- **Category:** Maintainability
- **Spec:** SPEC-007

**Description:**
All code, comments, identifiers, `requirements.md`, and `technical-specifications.md` are written in
English. Conversation with the user follows the user's language (French or English).

**Target metric:** 0 non-English identifiers or comments in source files; 0 non-English entries in
requirements or spec files.

**Acceptance criteria:**
- CLAUDE.md states language rules explicitly
- requirements-analyst writes all file content in English

---

## UI Requirements

<!-- UIR entries go here -->
