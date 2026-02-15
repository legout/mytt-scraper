---
id: ms-08nr
status: closed
deps: [ms-j0ge]
links: [ms-j0ge]
created: 2026-02-08T16:43:43Z
type: task
priority: 2
assignee: legout
external-ref: plan-choose-textual-for-creating-the-tui
tags: [tf, backlog, plan, component:docs, component:tui]
---
# Document how to run the Textual TUI

## Task

Add documentation for running the new TUI (install steps, how to start it, supported actions, and troubleshooting for headed/headless login).

## Context

Users should be able to discover and use the TUI without reading the code.

## Acceptance Criteria

- [ ] README or docs include TUI run instructions
- [ ] Mentions headless default and how to enable headed mode
- [ ] Lists supported workflows (login, fetch own, search, fetch selected)

## References

- Plan: plan-choose-textual-for-creating-the-tui


## Notes

**2026-02-14T09:27:40Z**

## Implementation Complete

Added comprehensive TUI documentation to README.md covering:

**TUI Run Instructions:**
-  command
- Alternative  command

**Headless/Headed Documentation:**
- Documented TUI runs headless-only
- Comparison table shows CLI scripts support headed mode
- Troubleshooting suggests using CLI with headed mode for debugging

**Supported Workflows Documented:**
1. Login Screen - credentials entry with progress indicators
2. Fetch My Profile - download own community data
3. Search Players - find by name with API/Playwright toggle
4. Fetch by User ID - download specific player data
5. Batch Fetch - multi-select and fetch with progress tracking

**Additional Sections:**
- TUI vs CLI comparison table
- Troubleshooting guide for common issues

**Commit:** bd5455a90844c4bb1e65b559319b0ebaf830bf68

**Review:** 0 Critical, 0 Major, 1 Minor (cosmetic), 2 Suggestions
