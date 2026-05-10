# Business Requirements

Business requirements (BRQ-NNN) for the **ferdi** project.
Linked to technical specifications in `technical-specifications.md`.

---

### BRQ-001 — Detect screen resolution

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-008

**User value:**
The user can trigger a voice command to detect and store the primary screen resolution for the current game session. The detected resolution is returned to the client.

**Description:**
A voice command ("detect resolution") is sent to the ferdi backend via HTTP. The backend detects the primary screen's resolution using a cross-platform library, stores it for later use (e.g., by Claude Vision for screenshot analysis), and returns the detected dimensions to the client. The client (VoiceAttack or other frontend) uses this response to vocally confirm the resolution to the user.

**Acceptance criteria:**
- [ ] A POST /detect-resolution endpoint exists
- [ ] The endpoint detects the primary monitor's resolution
- [ ] The detected resolution is stored in application state for later use
- [ ] The endpoint returns a 200 response with the detected resolution and a confirmation message
- [ ] The response format allows the client to extract and vocally confirm the resolution

### BRQ-002 — Set a quantum route by voice

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-009

**User value:**
The user can say "ferdi get a quantum route to [destination]" to automatically set a quantum route in Star Citizen, eliminating the need to manually open the star map, search, and confirm the destination.

**Description:**
A voice command is sent to the ferdi backend, which automatically opens the star map, searches for the requested destination, confirms the route was set, closes the star map, and activates quantum mode. Valid destinations are loaded from `etc/qt-destinations.yaml` at VoiceAttack startup to build the voice command's spoken list.

**Acceptance criteria:**
- [ ] A POST /quantum-route endpoint exists
- [ ] The endpoint accepts a destination name and orchestrates the full quantum route flow
- [ ] The endpoint verifies the screen resolution has been detected first
- [ ] The endpoint automatically opens the star map, searches for the destination, and closes the star map
- [ ] The endpoint activates quantum mode after a successful search
- [ ] The endpoint returns a confirmation message on success
- [ ] The endpoint returns an error message if the route could not be confirmed

### BRQ-003 — Screen screenshot command

- **Date:** 2026-05-05
- **Status:** Implemented
- **Validated:** 2026-05-05
- **Implemented:** 2026-05-05
- **Spec:** SPEC-011

**User value:**
The user can trigger a command to capture the full screen as a PNG image. The screenshot is automatically saved to a timestamped file in the `screenshots/` directory for later analysis by Claude Vision.

**Description:**
A voice command is sent to the ferdi backend via HTTP, which captures the full screen using a cross-platform library. The screenshot is saved to `screenshots/YYYY-MM-DD_HH-MM-SS.png` (with the actual current timestamp). The directory is created automatically if absent. The endpoint returns a confirmation message to the client. The capture logic is implemented as a reusable function (not inlined in the HTTP handler) so it can be called by other features later.

**Acceptance criteria:**
- [ ] A POST /screenshot endpoint exists
- [ ] The endpoint returns HTTP 200 with a JSON body `{"message": "screen is shot"}`
- [ ] The screenshot file exists on disk after the endpoint returns
- [ ] The `screenshots/` directory is created automatically if it does not exist
- [ ] The capture logic is a reusable function, not inlined in the handler
