Mark requirement $ARGUMENTS as validated by the user, authorizing the TDD cycle to begin.

## Expected input format

`/validate <REQ-ID>`

`<REQ-ID>` is one of: `BRQ-NNN`, `TRQ-NNN`, `NFR-NNN`, `UIR-NNN`

## Instructions

1. Read `requirements.md` and locate the heading `### <REQ-ID>:`.
2. Check that its current `**Status:**` is `Draft`. If it is anything else, report the current status and stop — do not change it.
3. Replace `**Status:** Draft` with `**Status:** Validated`.
4. Append the following line immediately after the status line (create it if it does not exist):
   `**Validated:** <today's date YYYY-MM-DD>`
5. Confirm to the user:
   - Requirement ID and title
   - Status changed from Draft → Validated
   - Next step: run `/tdd <REQ-ID>` to start the TDD cycle
