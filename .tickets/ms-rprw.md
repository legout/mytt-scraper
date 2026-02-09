---
id: ms-rprw
status: closed
deps: [ms-ij43]
links: [ms-ij43, ms-28lt]
created: 2026-02-08T16:43:42Z
type: task
priority: 2
assignee: legout
external-ref: plan-choose-textual-for-creating-the-tui
tags: [tf, backlog, plan, component:tui, component:auth, component:core]
---
# Implement Textual LoginScreen + background Playwright login

## Task

Implement a Login screen (username + masked password) and run Playwright login as a background task, reporting progress/errors in the UI.

## Context

Login uses Playwright and can take time (captcha, navigation). The UI must stay responsive.

## Acceptance Criteria

- [ ] LoginScreen collects username + password (password masked)
- [ ] Login runs in a background worker/task and updates status
- [ ] On success, an authenticated scraper/searcher instance is stored in app state
- [ ] On failure, error is shown and user can retry

## Constraints

- Credentials are session-only (no persistence)

## References

- Plan: plan-choose-textual-for-creating-the-tui


## Notes

**2026-02-08T17:22:20Z**

Implemented Textual LoginScreen with background Playwright login.

Changes:
- app.py: Added reactive scraper state and helper methods (set_scraper, set_searcher, clear_scraper, get_scraper, is_authenticated)
- screens.py: Rewrote LoginScreen with background worker-based login using Textual's Worker API

Features:
- Login runs in background worker (UI stays responsive during Playwright operations)
- Progress status updates during login
- On success: stores authenticated PlayerSearcher in app state, clears credentials from memory
- On failure: shows error and allows retry
- Credentials are session-only (no persistence)

Commit: 4aeb052
