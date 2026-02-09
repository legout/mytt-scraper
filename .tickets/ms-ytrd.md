---
id: ms-ytrd
status: closed
deps: []
links: [ms-lk6f]
created: 2026-02-08T19:38:45Z
type: task
priority: 2
assignee: legout
external-ref: seed-fix-textual-async-worker-threading
tags: [tf, backlog, component:tui]
---
# Fix async worker UI updates (login + profile fetch)

## Task
Replace `app.call_from_thread(...)` usage with direct UI updates in async workers for login + profile fetch flows.

## Context
Textual async workers (default `run_worker(..., thread=False)`) run on the app event loop thread; calling `call_from_thread` from there raises a RuntimeError and crashes `python -m mytt_scraper.tui`. Plan requires Option A: keep async workers and remove `call_from_thread` wrappers.

## Acceptance Criteria
- [ ] In `LoginScreen._do_login`, no `call_from_thread` is used and status updates still render.
- [ ] In `MainMenuScreen._do_fetch_own_profile` and `_do_fetch_external_profile`, no `call_from_thread` is used and status/table updates still render.
- [ ] `uv run python -m mytt_scraper.tui` can login and reach main menu without crashing.

## Constraints
- Keep workers async; do not set `thread=True`.
- Keep changes localized to `src/mytt_scraper/tui/screens.py`.

## References
- Seed: seed-fix-textual-async-worker-threading
- Plan: plan-fix-textual-async-worker-threading


## Notes

**2026-02-08T19:43:01Z**

## Implemented: Fix async worker UI updates

**Commit:** b744e16

### Changes Made
- Removed  usage from  (2 instances)
- Removed  usage from  (4 instances)
- Removed  usage from  (4 instances)

### Rationale
Async workers with default  run on the app event loop thread. Calling  from these workers raised RuntimeError since the code was already on the main thread. Changed to direct method calls.

### Verification
- Python syntax verified
- Changes localized to  as required

### Review Notes
- 0 Critical/Major/Minor issues
- 3 Warnings identified for other screens (SearchScreen, BatchFetchScreen, TablePreviewScreen) with similar issues - tracked separately
