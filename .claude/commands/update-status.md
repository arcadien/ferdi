Update the status of a requirement and its linked specification.

## Expected input format

`/update-status <REQ-ID> <new-status>`

`<REQ-ID>` is one of: `BRQ-NNN`, `TRQ-NNN`, `NFR-NNN`, `UIR-NNN`

Valid statuses: `Draft`, `In Progress`, `Implemented`, `Cancelled`

## Instructions

1. Parse the requirement ID and new status from $ARGUMENTS.
2. In `requirements.md`, find the heading `### <REQ-ID>:` and replace the `**Status:**` line beneath it.
3. In `technical-specifications.md`, find the `## SPEC-NNN` block whose heading contains `(<REQ-ID>)` and replace its `**Status:**` line.
4. Confirm the update: show the requirement ID, spec ID, old status, and new status.

If the ID is not found, report an error and list all existing requirement IDs grouped by type.
