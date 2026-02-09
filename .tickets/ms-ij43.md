---
id: ms-ij43
status: closed
deps: []
links: [ms-rprw]
created: 2026-02-08T16:43:42Z
type: task
priority: 2
assignee: legout
external-ref: plan-choose-textual-for-creating-the-tui
tags: [tf, backlog, plan, component:tui, component:deps]
---
# Add Textual dependency + TUI entrypoint skeleton

## Task

Add a new Textual-based TUI entrypoint and minimal app skeleton (screen routing only).

## Context

We want an app-like terminal UI (login screen, menus, selectable results). Textual provides screens/widgets and is a better fit than Rich-only output for this.

## Acceptance Criteria

- [ ] `textual` is added as a dependency
- [ ] A runnable entrypoint exists (e.g. `scripts/tui.py` or `python -m mytt_scraper.tui`)
- [ ] App starts and shows a placeholder screen (no scraping yet)
- [ ] Basic navigation structure is in place (screen switch scaffolding)

## Constraints

- Existing `scripts/main.py` remains unchanged

## References

- Plan: plan-choose-textual-for-creating-the-tui


## Notes

**2026-02-08T16:50:10Z**

## Implementation Complete

**Summary**: Added Textual dependency and TUI entrypoint skeleton with three placeholder screens.

**Changes**:
- Added  to pyproject.toml dependencies
- Created  package with module entrypoint ()
- Implemented LoginScreen, MainMenuScreen, and SearchScreen with navigation
- Added exception handling and __all__ exports per code review

**Review Issues**: 2 Critical + 3 Major fixed (exception handling, placeholder warnings, exports)

**Commit**: f926798

**Verification**:
-  - Textual 7.5.0 installed successfully
- Import test passes
- All acceptance criteria met
