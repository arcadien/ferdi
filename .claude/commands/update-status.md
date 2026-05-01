Update the status of requirement and specification $ARGUMENTS.

## Expected input format

`/update-status REQ-NNN <new-status>`

Valid statuses: `Draft`, `In Progress`, `Implemented`, `Cancelled`

## Instructions

1. Parse the requirement ID (e.g. REQ-003) and new status from $ARGUMENTS.
2. In `requirements.md`, find the line `**Status:** <current>` under the matching `## REQ-NNN` heading and replace it with `**Status:** <new-status>`.
3. In `technical-specifications.md`, find the matching `## SPEC-NNN` block (linked to the same REQ-NNN) and update its `**Status:**` line the same way.
4. Confirm the update to the user, showing old and new status for both files.

If the requirement ID is not found, report an error and list the existing REQ IDs.
