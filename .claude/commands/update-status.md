Update the status of a requirement and its linked specification.

## Expected input format

`/update-status <REQ-ID> <new-status>`

`<REQ-ID>` is one of: `BRQ-NNN`, `TRQ-NNN`, `NFR-NNN`, `UIR-NNN`

Valid statuses: `Draft`, `Validated`, `In Progress`, `Implemented`, `Refactored`, `Cancelled`

## Allowed transitions

| From | To |
|------|----|
| Draft | Validated, Cancelled |
| Validated | In Progress, Cancelled |
| In Progress | Implemented, Cancelled |
| Implemented | Refactored |
| Refactored | — (terminal) |
| Cancelled | — (terminal) |

Warn the user if the requested transition is not in the table above, but allow it if they confirm.

## Instructions

1. Parse the requirement ID and new status from $ARGUMENTS.
2. In `requirements.md`, find `### <REQ-ID>:` and replace its `**Status:**` line.
3. In `technical-specifications.md`, find the `## SPEC-NNN` block whose heading contains `(<REQ-ID>)` and replace its `**Status:**` line.
4. Confirm: show requirement ID, spec ID, old status → new status.

If the ID is not found, list all existing requirement IDs grouped by type.
