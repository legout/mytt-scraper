---
id: ms-lk6f
status: closed
deps: [ms-ytrd]
links: [ms-ytrd, ms-fp62]
created: 2026-02-08T19:38:45Z
type: task
priority: 2
assignee: legout
external-ref: seed-fix-textual-async-worker-threading
tags: [tf, backlog, component:tui]
---
# Fix async worker UI updates (search worker)

## Task
Remove `app.call_from_thread(...)` usage from the async search worker and use direct UI updates.

## Context
The TUI uses `run_worker()` with async functions. `call_from_thread` must only be used from `thread=True` workers; using it in async workers causes the runtime crash. This ticket covers the player search worker.

## Acceptance Criteria
- [ ] `_do_search(...)` contains no `call_from_thread` calls.
- [ ] Search still updates status and results table without exceptions.
- [ ] No regressions in switching between search and other screens.

## Constraints
- Do not change worker threading model (no `thread=True`).

## References
- Seed: seed-fix-textual-async-worker-threading
- Plan: plan-fix-textual-async-worker-threading


## Notes

**2026-02-08T19:44:39Z**

## Implemented: Fix async worker UI updates (search worker)

**Commit:** b2838f7

### Changes Made
- Removed 1 <code>call_from_thread</code> usage from <code>_do_search</code> in SearchScreen

### Rationale
Async workers with default <code>run_worker(..., thread=False)</code> run on the app event loop thread. Calling <code>call_from_thread</code> from these workers raised RuntimeError since the code was already on the main thread. Changed to direct method call following pattern from ms-ytrd.

### Verification
- Python syntax verified
- Change localized to single method as required
- Review passed with 0 issues
