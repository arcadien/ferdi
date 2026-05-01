Document the user request $ARGUMENTS as a formal requirement and write its technical specification.

## Instructions

### Step 1 — Assign a requirement ID

Read `requirements.md`. Find the highest existing REQ-NNN number and increment it by 1.
If the file is empty or has no requirements yet, start at REQ-001.

### Step 2 — Write the requirement entry

Append the following block to `requirements.md`:

```
## REQ-NNN: <short title>

**Date:** <today's date YYYY-MM-DD>
**Status:** Draft

### Description
<Clear one-paragraph description of what the user wants, written in English.>

### Acceptance Criteria
- [ ] <Measurable criterion 1>
- [ ] <Measurable criterion 2>
- [ ] <Add more as needed>
```

### Step 3 — Write the technical specification

Read `technical-specifications.md`. Find the highest existing SPEC-NNN number and increment by 1.
Append the following block to `technical-specifications.md`:

```
## SPEC-NNN: <short title> (REQ-NNN)

**Date:** <today's date YYYY-MM-DD>
**Status:** Draft

### Overview
<One paragraph explaining the technical approach.>

### Architecture
<Describe components involved, data flow, and integration points.>

### Implementation Plan
1. <Step 1>
2. <Step 2>
3. <Add more as needed>

### Files to Create or Modify
| File | Action | Purpose |
|------|--------|---------|
| `path/to/file` | create / modify | reason |

### Testing
<Describe how to validate each acceptance criterion.>
```

### Step 4 — Report

Tell the user which REQ-NNN and SPEC-NNN were created and briefly summarize what was documented.
