Execute the full TDD cycle for requirement $ARGUMENTS.

## Expected input format

`/tdd <REQ-ID>`

---

## Pre-condition check

Before starting, read `requirements.md` and check the status of `<REQ-ID>`:
- `Draft` → stop. Tell the user to run `/validate <REQ-ID>` first.
- `Implemented` or `Refactored` → stop. Tell the user the requirement is already done.
- `Validated` or `In Progress` → continue.

---

## Phase 1 — Write failing tests (RED)

**Delegate to the requirements-analyst agent:**

> Read `requirements.md` for `<REQ-ID>` and its linked SPEC in `technical-specifications.md`.
>
> Write one failing test per acceptance criterion.
> - Follow existing project test conventions (location, naming, framework).
> - Test names must reference the requirement ID (e.g. `test_brq001_description`).
> - Tests must fail with the current codebase. Do not write any implementation code.
> - Update `**Status:**` to `In Progress` in `requirements.md` and the linked SPEC in `technical-specifications.md`.
> - Return the list of test names written and the **exact file paths** of all files modified.

**Then delegate to the test-runner agent:**

> Run the test suite. Report the execution result.
> We expect the new tests to FAIL (RED). If any new test passes, flag it explicitly.

If any new test passes unexpectedly, delegate back to requirements-analyst to fix the test so it is properly RED before continuing.

**Once tests are confirmed RED, delegate to the git-manager agent:**

> Stage and commit the test files for `<REQ-ID>`.
> - Stage only the test file(s) returned by the requirements-analyst (do NOT stage `requirements.md` or `technical-specifications.md`)
> - Commit message: `test(<id>): write acceptance tests` (use requirement ID in lowercase as scope, e.g. `trq-003`)

Relay both agents' summaries and the git commit to the user.

**STOP. Ask the user:**
> Tests are written and committed. Proceed to implementation?

Wait for explicit user confirmation before continuing.

---

## Phase 2 — Implement (GREEN)

**Delegate to the requirements-analyst agent:**

> Implement the minimum code to make the failing tests for `<REQ-ID>` pass.
> Do not add behaviour beyond what the tests require.
> Return the **exact file paths** of all files created or modified (excluding `requirements.md` and `technical-specifications.md`).

**Then delegate to the test-runner agent:**

> Run the **full test suite**. Report the complete execution result.
> We need ALL tests to pass (GREEN), including pre-existing ones.

If any test is still RED: delegate back to requirements-analyst to fix, then re-run test-runner. Repeat until GREEN.

**Once all tests are GREEN, delegate to the git-manager agent:**

> Stage and commit the implementation files for `<REQ-ID>`.
> - Stage only the implementation file(s) returned by the requirements-analyst (do NOT stage test files, `requirements.md`, or `technical-specifications.md`)
> - Commit message: `feat(<id>): implement <title>` (use requirement ID in lowercase as scope)

Relay both agents' summaries and the git commit to the user.

**STOP. Ask the user:**
> All tests are GREEN. Do you want to run a refactor phase? (yes / no)

Wait for the user's answer.

---

## Phase 3 — Refactor (optional)

Only execute if the user answered **yes**.

**Delegate to the requirements-analyst agent:**

> Refactor the code produced for `<REQ-ID>`: improve readability, remove duplication, simplify logic.
> Do not change observable behaviour. Do not modify test files.
> Return the **exact file paths** of all files modified.

**Then delegate to the test-runner agent:**

> Run the full test suite. All tests must still be GREEN after refactor.

If any test went RED: tell the user and delegate back to requirements-analyst to revert or fix.

**Once GREEN after refactor, delegate to the git-manager agent:**

> Stage and commit the refactored files for `<REQ-ID>`.
> - Stage only the refactored implementation file(s) (do NOT stage test files, `requirements.md`, or `technical-specifications.md`)
> - Commit message: `refactor(<id>): <brief description of what was improved>`

Relay both agents' summaries and the git commit to the user.

---

## Closing

**Delegate to the requirements-analyst agent:**

> Update `**Status:**` in `requirements.md` for `<REQ-ID>`:
> - If refactor was done: set `Refactored`
> - Otherwise: set `Implemented`
> Do the same for the linked SPEC in `technical-specifications.md`.

**Then delegate to the git-manager agent:**

> Stage and commit the final status update for `<REQ-ID>`.
> - Stage `requirements.md` and `technical-specifications.md`
> - Commit message: `req(<id>): mark implemented` or `req(<id>): mark refactored` depending on outcome

Report the final status and commit to the user.
