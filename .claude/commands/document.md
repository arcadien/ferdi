Document the user request $ARGUMENTS as a formal requirement and its technical specification.

## Expected input format

`/document <type> <description>`

Valid types: `business`, `technical`, `nonfunctional`, `ui`

## Instructions

Delegate the entire task to the **requirements-analyst** agent with the following prompt:

> Document a new requirement of type `<type>` for this description: `<description>`.
>
> Steps:
> 1. Read `requirements.md` to find the next available ID for this type (BRQ / TRQ / NFR / UIR — each counter is independent).
> 2. Append the requirement entry under the correct section in `requirements.md` using the template for this type (see below).
> 3. Read `technical-specifications.md` to find the next SPEC-NNN number.
> 4. Append the linked technical specification to `technical-specifications.md`.
> 5. Return a summary with the assigned IDs and one-sentence description of what was documented.
>
> ### Templates
>
> **Business (BRQ-NNN)**
> ```
> ### BRQ-NNN: <title>
> **Date:** YYYY-MM-DD  **Status:** Draft
> #### Business Context
> <why it matters>
> #### Description
> <what is needed>
> #### Acceptance Criteria
> - [ ] criterion
> ```
>
> **Technical (TRQ-NNN)**
> ```
> ### TRQ-NNN: <title>
> **Date:** YYYY-MM-DD  **Status:** Draft
> #### Context
> <technical constraint or integration>
> #### Description
> <what must be true>
> #### Acceptance Criteria
> - [ ] criterion
> ```
>
> **Non-Functional (NFR-NNN)**
> ```
> ### NFR-NNN: <title>
> **Date:** YYYY-MM-DD  **Status:** Draft  **Category:** Performance|Security|Reliability|Maintainability|Scalability
> #### Description
> <quality attribute>
> #### Target Metric
> <concrete measurable threshold>
> #### Acceptance Criteria
> - [ ] criterion
> ```
>
> **UI (UIR-NNN)**
> ```
> ### UIR-NNN: <title>
> **Date:** YYYY-MM-DD  **Status:** Draft
> #### User Story
> As a <role>, I want <action> so that <benefit>.
> #### Description
> <interaction or visual detail>
> #### UX Criteria
> - [ ] criterion
> ```
>
> **Specification (SPEC-NNN)**
> ```
> ## SPEC-NNN: <title> (<REQ-ID>)
> **Date:** YYYY-MM-DD  **Status:** Draft  **Requirement type:** <type>
> ### Overview
> ### Architecture
> ### Implementation Plan
> 1. step
> ### Files to Create or Modify
> | File | Action | Purpose |
> ### Testing
> ```

After the agent completes, delegate to the **git-manager** agent:

> Stage and commit the new requirement.
> - Stage `requirements.md` and `technical-specifications.md`
> - Commit message: `req(<id>): document <title>` (use the requirement ID in lowercase as scope, e.g. `trq-003`)

After git-manager confirms the commit, relay the requirements-analyst summary to the user and remind them:
> Requirement is in **Draft** status. Review the entries in `requirements.md` and `technical-specifications.md`, then run `/validate <REQ-ID>` to approve it.
