# Spike workflow

A **spike** is a time-boxed experiment on an isolated branch. Its goal is to validate a technical approach before committing to a formal requirement.

## Rules

- Branch off `main` with a `spike/<topic>` name (e.g. `spike/whisper-stt`)
- No `requirements.md` or `technical-specifications.md` entries — spikes are requirement-free
- No mandatory tests — exploration code is throwaway
- No conventional commit enforcement — commit messages can be informal
- The branch is **never merged** into `main`

## Outcome

| Result | Action |
|--------|--------|
| Success | Discard the branch. Document learnings as one or more requirements (Draft status). Start a clean TDD cycle on `main`. |
| Failure | Discard the branch. Note what was ruled out in conversation so it informs future requirements. |

## When to propose a spike

Propose a spike when:
- The right technical approach is genuinely unknown
- A library or API needs hands-on validation before committing to it
- Estimating effort requires a working prototype

Do **not** use a spike to avoid writing requirements. If the approach is already known, go straight to the TDD cycle.
