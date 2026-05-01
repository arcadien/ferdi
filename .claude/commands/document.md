Document the user request $ARGUMENTS as a formal requirement and write its technical specification.

## Expected input format

`/document <type> <description>`

Valid types: `business`, `technical`, `nonfunctional`, `ui`

## ID prefixes per type

| Type | Prefix | Counter in requirements.md |
|------|--------|---------------------------|
| business | BRQ-NNN | highest existing BRQ-NNN |
| technical | TRQ-NNN | highest existing TRQ-NNN |
| nonfunctional | NFR-NNN | highest existing NFR-NNN |
| ui | UIR-NNN | highest existing UIR-NNN |

Each counter is independent. If no entry exists for a type yet, start at 001.

## Step 1 — Parse input

Extract the type and description from $ARGUMENTS.
If the type is missing or invalid, stop and ask the user to specify one of: `business`, `technical`, `nonfunctional`, `ui`.

## Step 2 — Assign the requirement ID

Read `requirements.md`. Scan all headings to find the highest existing NNN for the chosen prefix. Increment by 1 to get the new ID.

## Step 3 — Write the requirement entry

Append the block for the matching type to `requirements.md`, under the appropriate section heading (create the section if it does not exist yet: `## Business Requirements`, `## Technical Requirements`, `## Non-Functional Requirements`, `## UI Requirements`).

### Business requirement template

```
### BRQ-NNN: <short title>

**Date:** <YYYY-MM-DD>
**Status:** Draft

#### Business Context
<Why this matters to the product or stakeholders.>

#### Description
<What the user or business needs.>

#### Acceptance Criteria
- [ ] <Measurable criterion 1>
- [ ] <Measurable criterion 2>
```

### Technical requirement template

```
### TRQ-NNN: <short title>

**Date:** <YYYY-MM-DD>
**Status:** Draft

#### Context
<Technical constraint or integration driving this requirement.>

#### Description
<What must be true at the technical level.>

#### Acceptance Criteria
- [ ] <Measurable criterion 1>
- [ ] <Measurable criterion 2>
```

### Non-functional requirement template

```
### NFR-NNN: <short title>

**Date:** <YYYY-MM-DD>
**Status:** Draft
**Category:** Performance | Security | Reliability | Maintainability | Scalability | Accessibility

#### Description
<Quality attribute that must be satisfied.>

#### Target Metric
<Concrete, measurable threshold (e.g. "p99 latency < 200 ms under 100 concurrent users").>

#### Acceptance Criteria
- [ ] <Measurable criterion 1>
- [ ] <Measurable criterion 2>
```

### UI requirement template

```
### UIR-NNN: <short title>

**Date:** <YYYY-MM-DD>
**Status:** Draft

#### User Story
As a <role>, I want <action> so that <benefit>.

#### Description
<Detailed description of the interaction or visual element.>

#### UX Criteria
- [ ] <Interaction or visual criterion 1>
- [ ] <Interaction or visual criterion 2>
```

## Step 4 — Write the technical specification

Read `technical-specifications.md`. Find the highest existing SPEC-NNN and increment by 1.
Append the block below, using the correct requirement ID (BRQ/TRQ/NFR/UIR).

```
## SPEC-NNN: <short title> (<REQ-ID>)

**Date:** <YYYY-MM-DD>
**Status:** Draft
**Requirement type:** business | technical | nonfunctional | ui

### Overview
<One paragraph explaining the technical approach.>

### Architecture
<Components involved, data flow, integration points.>

### Implementation Plan
1. <Step 1>
2. <Step 2>
3. <Add more as needed>

### Files to Create or Modify
| File | Action | Purpose |
|------|--------|---------|
| `path/to/file` | create / modify | reason |

### Testing
<How to validate each acceptance criterion from the linked requirement.>
```

## Step 5 — Report

Tell the user the assigned IDs (e.g. BRQ-002 / SPEC-004) and a one-sentence summary of what was documented.
