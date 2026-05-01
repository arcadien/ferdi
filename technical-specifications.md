# Technical Specifications

This file contains the technical specification for each requirement documented in `requirements.md`.
Each specification is assigned a unique ID (SPEC-NNN) and references its parent requirement (REQ-NNN).

Specifications are created via the `/document` command. Together with `requirements.md`, they provide
enough information to automate or reproduce any implementation independently.

---

## SPEC-001 — Requirement-driven development

- **Requirement:** BRQ-001
- **Date:** 2026-05-01
- **Status:** Implemented

### Overview

The ferdi project enforces a strict requirement-first workflow. No code may be written until the
corresponding requirement has been documented and validated by the user. The two markdown files
`requirements.md` and `technical-specifications.md` together constitute the single source of truth
for every feature in the project.

### Architecture

The workflow is enforced through convention and tooling:

1. The user issues a `/document` command to create a requirement entry (status: Draft).
2. The user reviews the entry and issues `/validate` to approve it (status: Validated).
3. Only after validation may the `/tdd` command begin the implementation cycle.
4. The agent system (requirements-analyst + test-runner) enforces the ordering.

### Implementation plan

- `requirements.md` holds all requirement entries grouped by type (BRQ / TRQ / NFR / UIR).
- `technical-specifications.md` holds all SPEC entries, one per requirement.
- Both files must be updated atomically: creating a requirement always creates its linked spec.
- CLAUDE.md documents the workflow rules so they are enforced by any agent reading the project.

### Files

| File | Role |
|------|------|
| `requirements.md` | Authoritative list of all requirements |
| `technical-specifications.md` | Implementation-level detail for each requirement |
| `CLAUDE.md` | Project rules including the requirement-first workflow |

### Testing approach

This requirement governs the process, not a runtime behaviour. Compliance is verified by inspection:
- Every implemented feature must have a corresponding BRQ / TRQ / NFR / UIR entry at status
  Implemented or Refactored.
- No source file may be introduced without a traceable requirement ID.

---

## SPEC-002 — Typed requirement management with independent ID counters

- **Requirement:** TRQ-001
- **Date:** 2026-05-01
- **Status:** Implemented

### Overview

Requirements are typed and identified by a prefix that encodes their category. Each prefix maintains
its own numeric counter, starting at 001. The four prefixes are BRQ (business), TRQ (technical),
NFR (non-functional), and UIR (UI). A fifth counter, SPEC, is used exclusively for technical
specifications.

### Architecture

ID assignment is done by the requirements-analyst agent when processing a `/document` command. The
agent scans the existing entries in `requirements.md` to determine the next available number for the
given prefix.

Counter independence example:

```
BRQ-001   ← first business requirement
TRQ-001   ← first technical requirement (counter resets per type)
TRQ-002   ← second technical requirement
NFR-001   ← first non-functional requirement
SPEC-001  ← spec for BRQ-001 (independent counter)
```

### Requirement entry template

Each requirement entry in `requirements.md` follows this structure:

```markdown
### <PREFIX>-NNN — <Short title>

- **Date:** YYYY-MM-DD
- **Validated:** YYYY-MM-DD
- **Status:** <Draft | Validated | In Progress | Implemented | Refactored | Cancelled>
- **Spec:** SPEC-NNN

**Description:**
<One or two sentences.>

**<Type-specific field>:**
<Business context / Technical constraint / Target metric / User story>

**Acceptance criteria:**
- <criterion 1>
- <criterion 2>
```

Type-specific field per type:

| Type | Field label |
|------|-------------|
| Business (BRQ) | Business context |
| Technical (TRQ) | Technical constraint |
| Non-Functional (NFR) | Target metric |
| UI (UIR) | User story |

### Files

| File | Role |
|------|------|
| `requirements.md` | Contains all typed requirement entries |

### Testing approach

Verified by inspection: no two requirements of the same type share a suffix; no requirement of
different types share a prefix-suffix pair; each entry contains all required fields.

---

## SPEC-003 — Technical specification linked to each requirement

- **Requirement:** TRQ-002
- **Date:** 2026-05-01
- **Status:** Implemented

### Overview

Every requirement has exactly one linked SPEC entry. The SPEC counter is independent of all
requirement counters. A SPEC is always created in the same `/document` invocation as its parent
requirement.

### Architecture

The SPEC entry in `technical-specifications.md` is structured as follows:

```markdown
## SPEC-NNN — <Short title matching parent requirement>

- **Requirement:** <REQ-ID>
- **Date:** YYYY-MM-DD
- **Status:** <mirrors parent requirement status>

### Overview
<Purpose and scope of the feature.>

### Architecture
<Design decisions, data flow, component interactions.>

### Implementation plan
<Step-by-step or bullet list of what must be built.>

### Files

| File | Role |
|------|------|
| `path/to/file` | What it contains or does |

### Testing approach
<How to verify the requirement is met; what tests cover it.>
```

### Implementation plan

- When `/document` is called, requirements-analyst writes both the requirement entry and its SPEC
  entry atomically.
- The SPEC status must be updated whenever the parent requirement status changes.
- The SPEC counter increments globally (not per-type), starting at SPEC-001.

### Files

| File | Role |
|------|------|
| `technical-specifications.md` | Contains all SPEC entries |

### Testing approach

Verified by inspection: for every requirement entry in `requirements.md`, a corresponding SPEC-NNN
entry exists in `technical-specifications.md` with a matching `Requirement:` back-reference.

---

## SPEC-004 — Claude Code custom commands for the development workflow

- **Requirement:** TRQ-003
- **Date:** 2026-05-01
- **Status:** Implemented

### Overview

Four slash commands drive the entire development lifecycle. They are defined as markdown files under
`.claude/commands/` and are loaded automatically by Claude Code. Each command orchestrates one or
more sub-agents to perform its work.

### Architecture

**Command files and their roles:**

| File | Command | Role |
|------|---------|------|
| `.claude/commands/document.md` | `/document <type> <description>` | Invokes requirements-analyst to create a requirement entry (status: Draft) and its linked SPEC entry |
| `.claude/commands/validate.md` | `/validate <REQ-ID>` | Invokes requirements-analyst to set the requirement and its SPEC to Validated |
| `.claude/commands/tdd.md` | `/tdd <REQ-ID>` | Orchestrates the full TDD cycle (see below) |
| `.claude/commands/update-status.md` | `/update-status <REQ-ID> <status>` | Invokes requirements-analyst to set an arbitrary status |

**`/tdd` orchestration pattern:**

```
/tdd <REQ-ID>
  │
  ├─ 1. requirements-analyst reads the requirement and its SPEC
  │
  ├─ 2. requirements-analyst writes tests (Phase 1 — RED)
  │      Status set to: In Progress
  │
  ├─ 3. test-runner runs the full test suite
  │      Expected result: at least one new test FAILS
  │
  ├─ [CHECKPOINT] User confirms tests are RED before proceeding
  │
  ├─ 4. requirements-analyst writes minimum implementation (Phase 2 — GREEN)
  │
  ├─ 5. test-runner runs the full test suite
  │      Expected result: all tests PASS
  │      Status set to: Implemented
  │
  └─ [OPTIONAL] Refactor phase
       requirements-analyst refactors code
       test-runner re-runs suite → must stay GREEN
       Status set to: Refactored
```

### Implementation plan

- Create `.claude/commands/document.md` with argument parsing for `<type>` and `<description>`.
- Create `.claude/commands/validate.md` with argument parsing for `<REQ-ID>`.
- Create `.claude/commands/tdd.md` implementing the multi-phase orchestration described above.
- Create `.claude/commands/update-status.md` with argument parsing for `<REQ-ID>` and `<status>`.

### Files

| File | Role |
|------|------|
| `.claude/commands/document.md` | `/document` command definition |
| `.claude/commands/validate.md` | `/validate` command definition |
| `.claude/commands/tdd.md` | `/tdd` command definition |
| `.claude/commands/update-status.md` | `/update-status` command definition |

### Testing approach

Verified by inspection and manual invocation:
- All four files exist and are valid markdown.
- `/document` creates both a requirement entry and a SPEC entry.
- `/tdd` does not proceed to implementation without a RED test confirmation.
- `/update-status` accepts any valid status string.

---

## SPEC-005 — Two specialized sub-agents

- **Requirement:** TRQ-004
- **Date:** 2026-05-01
- **Status:** Implemented

### Overview

Two sub-agents are defined in `.claude/agents/`. Their capabilities are deliberately limited by
their tool declarations so that responsibilities cannot bleed across agents. The separation enforces
the principle that writing code and running code are distinct operations.

### Architecture

**requirements-analyst**

- **Tools:** Read, Write, Edit
- **No shell access** (Bash is not in its tool list)
- **Responsibilities:**
  - Write and update `requirements.md` and `technical-specifications.md`
  - Write test code (TDD Phase 1)
  - Write implementation code (TDD Phase 2)
  - Refactor code (TDD Phase 3)
  - Update requirement and spec statuses

**test-runner**

- **Tools:** Bash, Read
- **No file-write access** (Write and Edit are not in its tool list)
- **Responsibilities:**
  - Discover and run the full test suite
  - Report RED / GREEN status using a structured output format

**test-runner output format:**

```
## Test Run — <REQ-ID> — <PASS|FAIL>

| Test | Status | Detail |
|------|--------|--------|
| test_name_here | PASS | — |
| test_name_here | FAIL | AssertionError: expected X got Y |

Summary: N passed, M failed
```

### Implementation plan

- Create `.claude/agents/requirements-analyst.md` declaring tools: Read, Write, Edit and
  documenting the agent's responsibilities and output conventions.
- Create `.claude/agents/test-runner.md` declaring tools: Bash, Read and documenting the structured
  output format the agent must produce.

### Files

| File | Role |
|------|------|
| `.claude/agents/requirements-analyst.md` | Agent definition: tools, responsibilities, output conventions |
| `.claude/agents/test-runner.md` | Agent definition: tools, output format, RED/GREEN reporting |

### Testing approach

Verified by inspection:
- Each agent file declares only its permitted tools.
- The test-runner output format specification matches what the `/tdd` command expects to parse for
  RED/GREEN determination.

---

## SPEC-006 — TDD enforcement — tests before implementation

- **Requirement:** NFR-001
- **Date:** 2026-05-01
- **Status:** Implemented

### Overview

The TDD discipline is enforced at the workflow level, not at the runtime level. The `/tdd` command
is the sole entry point for implementing a requirement, and its internal sequencing makes it
structurally impossible to reach the implementation phase without first producing failing tests.

### Architecture

Enforcement mechanism within `/tdd`:

1. Phase 1 (RED): requirements-analyst writes test code only. No production code is touched.
2. Checkpoint: test-runner runs the suite. The command explicitly checks for at least one failing
   test. If all tests pass (which would indicate tests were not written or the feature already
   exists), the user is notified and the command does not proceed automatically.
3. User confirmation: the user must explicitly approve the RED state before Phase 2 begins.
4. Phase 2 (GREEN): requirements-analyst writes the minimum implementation to make tests pass.
5. Verification: test-runner runs the full suite. The requirement is only marked Implemented when
   all tests pass — including pre-existing tests, not just the new ones.
6. Phase 3 (optional): refactor only after full GREEN suite; suite must remain GREEN throughout.

### Implementation plan

- The enforcement is embedded in `.claude/commands/tdd.md` as explicit sequencing steps.
- The requirements-analyst agent definition documents that implementation code is only written in
  Phase 2, after RED confirmation.
- The test-runner agent reports a structured summary that the `/tdd` orchestrator uses to determine
  RED/GREEN state.

### Files

| File | Role |
|------|------|
| `.claude/commands/tdd.md` | Enforces RED → GREEN → (optional) REFACTOR sequencing |
| `.claude/agents/requirements-analyst.md` | Documents phased responsibilities |
| `.claude/agents/test-runner.md` | Produces RED/GREEN verdict consumed by `/tdd` |

### Testing approach

Verified by process inspection:
- The `/tdd` command definition contains an explicit checkpoint between Phase 1 and Phase 2.
- The checkpoint requires a non-zero failure count from test-runner before proceeding.
- The full suite (not a subset) is run at each checkpoint.

---

## SPEC-007 — Language consistency

- **Requirement:** NFR-002
- **Date:** 2026-05-01
- **Status:** Implemented

### Overview

The ferdi project operates across two languages: English for all technical artifacts, and the user's
language (French or English) for conversational responses. This rule is unconditional for written
artifacts and must be respected by every agent.

### Architecture

The rule is declared in `CLAUDE.md` under the section "Language rules" and is therefore visible to
every agent that reads the project instructions. No runtime enforcement mechanism is needed; the
rule is part of the agent's operating instructions.

Scope of "English only":
- All source code files (Python, YAML, TOML, etc.)
- All comments within source files
- All identifier names (variables, functions, classes, modules)
- `requirements.md`
- `technical-specifications.md`
- Agent definition files under `.claude/agents/`
- Command definition files under `.claude/commands/`

Scope of "follow the user's language":
- Chat responses in the Claude Code conversation window
- Inline explanations produced during a session (not written to files)

### Implementation plan

- `CLAUDE.md` contains the "Language rules" section as the authoritative declaration.
- requirements-analyst agent definition explicitly restates the rule so the agent applies it when
  writing file content.
- No tooling enforcement is required beyond the instruction.

### Files

| File | Role |
|------|------|
| `CLAUDE.md` | Authoritative language rule declaration |
| `.claude/agents/requirements-analyst.md` | Restates rule for file-writing agent |

### Testing approach

Verified by inspection:
- `CLAUDE.md` contains an explicit "Language rules" section covering both the English-only scope
  and the user-language conversation scope.
- A review of all files in the repository finds no non-English identifiers or comments.
