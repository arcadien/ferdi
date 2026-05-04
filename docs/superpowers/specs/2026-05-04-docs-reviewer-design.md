# Design: docs-reviewer agent

- **Date:** 2026-05-04
- **Status:** Approved
- **Branch:** fix/docs-stale-references

## Problem

After a requirement is implemented, `requirements.md` and `technical-specifications.md` can accumulate stale entries: outdated file references, misclassified requirements, broken REQ↔SPEC links, and inconsistent statuses. These issues are not caught by the TDD cycle and surface only during manual review.

## Solution

Add a mandatory **Phase 4 — Documentation review** to the development workflow, executed by a new `docs-reviewer` agent before git-manager creates any PR. The agent reads both documentation files, runs six consistency checks, and either green-lights the PR or blocks it with a structured report.

## Workflow Integration

The review inserts between implementation completion and PR creation:

```
Phase 1 — RED     → test-writer + test-runner
Phase 2 — GREEN   → implementer + test-runner
Phase 3 — Refactor (optional, user must request)
Phase 4 — Docs review → docs-reviewer          ← new mandatory phase
           GREEN → git-manager creates PR
           RED   → report surfaced to user → fix or waive → re-run
```

**Rule:** git-manager must not create a PR until docs-reviewer returns GREEN or the user has explicitly waived each reported issue.

## Agent Specification

| Attribute | Value |
|-----------|-------|
| Name | `docs-reviewer` |
| File | `.claude/agents/docs-reviewer.md` |
| Model | Haiku |
| Tools | Read, Grep, Glob — no Write, no Bash |
| Writes to | Nothing |

## Checks

The agent reads `requirements.md` and `technical-specifications.md` and applies the following checks:

| # | Check | Example anomaly caught |
|---|-------|------------------------|
| 1 | **Prefix classification** | TRQ-NNN entry found outside the Technical Requirements section |
| 2 | **Bidirectional REQ↔SPEC links** | BRQ-002 cites SPEC-009 but SPEC-009 does not list BRQ-002 as a parent requirement |
| 3 | **Status consistency** | Requirement marked `Implemented` but linked SPEC still `In Progress` |
| 4 | **Cross-file references** | `requirements.md` says `qt-destinations.txt`, `technical-specifications.md` says `qt-destinations.yaml` |
| 5 | **Checkbox format** | Acceptance criteria use `[x]` instead of the standard `[ ]` |
| 6 | **Orphan SPECs** | SPEC-NNN in `technical-specifications.md` with no corresponding requirement |

## Output Format

**GREEN:**
```
Documentation review passed. All 6 checks clean.
```

**RED:**
```
Documentation review FAILED. N issue(s) found:

[CHECK 1 — Prefix classification]
  TRQ-011 is listed under "Non-Functional Requirements" (line 342).
  Expected section: "Technical Requirements".

[CHECK 4 — Cross-file references]
  BRQ-002 (requirements.md) references `qt-destinations.txt`.
  SPEC-009 (technical-specifications.md) references `qt-destinations.yaml`.
  These must match.
```

## Escalation Protocol

On RED, the orchestrator surfaces the full report to the user with two options per issue:

- **Fix** — delegate corrections to requirements-analyst, then re-run docs-reviewer
- **Waive** — user explicitly acknowledges the issue and accepts it; git-manager proceeds but includes a "Waived issues" section in the PR body for traceability

A waiver is never silent. It must appear in the PR description.

## Files to Create or Modify

| File | Action |
|------|--------|
| `.claude/agents/docs-reviewer.md` | Create — agent definition |
| `.claude/workflow.md` | Modify — add Phase 4 to the development workflow |
