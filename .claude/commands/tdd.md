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
> - Return the list of test names written and the files modified.

**Then delegate to the test-runner agent:**

> Run the test suite. Report the execution result.
> We expect the new tests to FAIL (RED). If any new test passes, flag it explicitly.

Relay both agents' summaries to the user.

**STOP. Ask the user:**
> Tests are written. Are they RED as expected? Confirm to proceed to implementation, or describe what needs to be fixed.

Wait for explicit user confirmation before continuing.

---

## Phase 2 — Implement (GREEN)

**Delegate to the requirements-analyst agent:**

> Implement the minimum code to make the failing tests for `<REQ-ID>` pass.
> Do not add behaviour beyond what the tests require.
> Return the list of files created or modified.

**Then delegate to the test-runner agent:**

> Run the **full test suite**. Report the complete execution result.
> We need ALL tests to pass (GREEN), including pre-existing ones.

Relay both agents' summaries to the user.

If any test is still RED: delegate back to requirements-analyst to fix, then re-run test-runner. Repeat until GREEN.

Once GREEN, **STOP. Ask the user:**
> All tests are GREEN. Do you want to run a refactor phase? (yes / no)

Wait for the user's answer.

---

## Phase 3 — Refactor (optional)

Only execute if the user answered **yes**.

**Delegate to the requirements-analyst agent:**

> Refactor the code produced for `<REQ-ID>`: improve readability, remove duplication, simplify logic.
> Do not change observable behaviour. Do not modify test files.
> Return a list of changes made.

**Then delegate to the test-runner agent:**

> Run the full test suite. All tests must still be GREEN after refactor.

Relay both agents' summaries to the user.

If any test went RED: tell the user and delegate back to requirements-analyst to revert or fix.

---

## Closing

**Delegate to the requirements-analyst agent:**

> Update `**Status:**` in `requirements.md` for `<REQ-ID>`:
> - If refactor was done: set `Refactored`
> - Otherwise: set `Implemented`
> Do the same for the linked SPEC in `technical-specifications.md`.

Report the final status to the user.
