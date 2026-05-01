Mark requirement $ARGUMENTS as validated by the user.

## Expected input format

`/validate <REQ-ID>`

## Instructions

Delegate to the **requirements-analyst** agent with this prompt:

> Mark `<REQ-ID>` as Validated.
>
> 1. Read `requirements.md` and locate `### <REQ-ID>:`.
> 2. If status is not `Draft`, stop and report the current status — do not change it.
> 3. Replace `**Status:** Draft` with `**Status:** Validated`.
> 4. Add `**Validated:** <today YYYY-MM-DD>` on the next line.
> 5. Return a summary: requirement ID, title, status change, and confirmation.

After the agent completes, relay the result and tell the user:
> Requirement is now **Validated**. You can start the TDD cycle with `/tdd <REQ-ID>`.
