# Non-Functional Requirements

Non-functional requirements (NFR-NNN) for the **ferdi** project.
Linked to technical specifications in `technical-specifications.md`.

---

### NFR-001 — Cross-platform screen detection

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-008

**Non-functional requirement:**
Screen resolution detection must work consistently on Windows and Linux (X11/Wayland) without using platform-specific APIs.

**Description:**
The screen resolution detection mechanism must use only cross-platform libraries (e.g. screeninfo) and avoid platform-specific APIs such as ctypes.windll (Windows) or Xlib-specific calls (Linux). This ensures the codebase remains maintainable, testable, and portable across operating systems.

**Acceptance criteria:**
- [ ] The implementation uses only the `screeninfo` library (or equivalent cross-platform library)
- [ ] No Windows-specific APIs (e.g., ctypes.windll) appear in the implementation
- [ ] No Linux-specific direct system calls appear in the implementation
- [ ] Tests pass on Windows and Linux environments
- [ ] The same code path is used on both platforms

### NFR-002 — UI coordinates as screen percentage

- **Date:** 2026-05-03
- **Status:** Implemented
- **Validated:** 2026-05-03
- **Implemented:** 2026-05-03
- **Spec:** SPEC-009

**Non-functional requirement:**
All UI element positions must be expressed as a percentage of screen width and height, not absolute pixels, to ensure the same configuration works at any screen resolution without modification.

**Description:**
The quantum-route endpoint must calculate absolute screen coordinates from percentage values using the stored resolution. All UI positions in `etc/sc-config.yaml` must be percentages (0.0 to 1.0 range), and the endpoint converts these to absolute coordinates before moving the mouse or interacting with UI elements. This allows players with different monitor resolutions to use the same configuration file.

**Acceptance criteria:**
- [ ] The endpoint reads UI positions as percentages from the config file
- [ ] The endpoint calculates absolute coordinates using: `absolute_x = resolution.width * percentage_x`
- [ ] All UI coordinate values in the implementation use this percentage-based approach
- [ ] Tests verify correct conversion at multiple resolutions (e.g., 1920x1080, 2560x1440)
- [ ] Configuration documentation explains the percentage format clearly

### NFR-003 — Ruff linter and formatter

- **Date:** 2026-05-05
- **Status:** Validated
- **Validated:** 2026-05-05
- **Spec:** SPEC-012

**Non-functional requirement:**
All Python source files must pass `ruff check` (lint) and `ruff format --check` (format) with default settings. Ruff acts as both the linter and the formatter, replacing any ad-hoc style enforcement.

**Description:**
Ruff is a high-performance, Rust-based Python linter and formatter that replaces multiple tools (pylint, black, isort, flake8, etc.) with a single, fast, unified tool. The ferdi project adopts ruff to enforce consistent code style and catch common errors automatically. Ruff is installed as a dev dependency, configured with default settings (no custom rule overrides), and integrated into the pre-commit workflow and CI pipeline. This ensures that all code merged into main passes both linting and formatting checks.

**Acceptance criteria:**
- [ ] `ruff` is listed as a dev dependency in `pyproject.toml`
- [ ] `ruff check ferdi/ tests/` exits 0 on the codebase
- [ ] `ruff format --check ferdi/ tests/` exits 0 on the codebase
- [ ] Pre-commit hook `ruff check --fix` runs before each commit
- [ ] Pre-commit hook `ruff format` runs before each commit
- [ ] CI workflow includes both `ruff check` and `ruff format --check` steps
