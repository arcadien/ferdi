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

Warn the user if the requested transition is not listed above, but allow it if they confirm.

## Instructions

Delegate to the **requirements-analyst** agent:

> Update the status of `<REQ-ID>` to `<new-status>`.
> 1. In `requirements.md`, find `### <REQ-ID>:` and replace its `**Status:**` line.
> 2. In `technical-specifications.md`, find the `## SPEC-NNN` block containing `(<REQ-ID>)` and replace its `**Status:**` line.
> 3. Return: requirement ID, spec ID, old status, new status.
>
> If the ID is not found, list all existing requirement IDs grouped by type.

Relay the agent's result to the user.
