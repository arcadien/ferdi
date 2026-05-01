Execute the full TDD cycle for requirement $ARGUMENTS: write failing tests, implement, verify all tests pass, then offer a refactor phase.

## Expected input format

`/tdd <REQ-ID>`

## Pre-condition check

Read `requirements.md`. Locate `### <REQ-ID>:` and check `**Status:**`.
- If status is `Draft`: stop. Tell the user the requirement must be validated first (`/validate <REQ-ID>`).
- If status is `Validated` or `In Progress`: continue.
- If status is `Implemented` or `Refactored`: stop. Tell the user the requirement is already done.

Read `technical-specifications.md` and locate the linked `SPEC-NNN` block. Use it to guide test and implementation decisions.

---

## Phase 1 — Write failing tests (RED)

1. Based on the acceptance criteria in the requirement and the specification in `technical-specifications.md`, write one test per acceptance criterion.
2. Tests must be placed in the appropriate test file(s) for this project. Follow existing test conventions (file location, naming, framework).
3. Each test must:
   - Have a name that maps clearly to an acceptance criterion (e.g. `test_brq001_lands_on_pad_when_requested`)
   - Be written to FAIL with the current codebase (no implementation yet)
   - Assert the observable behaviour, not implementation details
4. After writing all tests, run them:
   ```
   <test command for this project>
   ```
5. Confirm the tests are RED (failing). If any test passes unexpectedly, investigate — it may mean the behaviour already exists or the test is not asserting correctly. Fix before continuing.
6. Update `**Status:**` in `requirements.md` to `In Progress`.
7. Report to the user:
   - List of test names written
   - Test run output confirming RED state
   - Ask the user to confirm before proceeding to implementation

**Wait for user confirmation before starting Phase 2.**

---

## Phase 2 — Implement (GREEN)

1. Write the minimum code needed to make the failing tests pass. Do not add behaviour beyond what the tests require.
2. Run the **full test suite** (not just the new tests):
   ```
   <test command for this project>
   ```
3. All tests must be GREEN.
   - If new tests still fail: fix the implementation, repeat.
   - If previously passing tests now fail: fix the regression before continuing.
4. Once all tests are green, report:
   - Full test run output
   - Files created or modified
   - Ask the user: "All tests are green. Do you want to proceed with a refactor? (yes / no)"

**Wait for user answer before starting Phase 3.**

---

## Phase 3 — Refactor (optional)

Only execute if the user answered yes.

1. Refactor the code produced in Phase 2: improve readability, remove duplication, simplify logic. Do not change behaviour.
2. After every meaningful change, run the full test suite and confirm it stays GREEN.
3. If any test goes RED during refactor: revert the last change and report to the user.
4. Once refactor is complete and tests are GREEN:
   - Update `**Status:**` in `requirements.md` to `Refactored`
   - Update the matching `SPEC-NNN` status in `technical-specifications.md` to `Refactored`
   - Report a summary of refactor changes

If the user skipped refactor:
- Update `**Status:**` in `requirements.md` to `Implemented`
- Update the matching `SPEC-NNN` status in `technical-specifications.md` to `Implemented`
- Report implementation summary
