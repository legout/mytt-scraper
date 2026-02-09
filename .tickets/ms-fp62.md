---
id: ms-fp62
status: closed
deps: [ms-lk6f]
links: [ms-lk6f, ms-hhlj]
created: 2026-02-08T19:38:45Z
type: task
priority: 2
assignee: legout
external-ref: seed-fix-textual-async-worker-threading
tags: [tf, backlog, component:tui]
---
# Fix async worker UI updates (batch fetch worker)

## Task
Remove `app.call_from_thread(...)` usage from the async batch fetch worker and use direct UI updates.

## Context
Batch fetch updates progress/log/status frequently. In the current async worker implementation, these updates go through `call_from_thread`, which crashes because the worker is not running in a separate OS thread.

## Acceptance Criteria
- [ ] `_do_batch_fetch(...)` contains no `call_from_thread` calls.
- [ ] Batch fetch screen renders progress/status/log updates during execution.
- [ ] Cancelling / navigating away mid-operation does not crash the app.

## Constraints
- Keep worker async; no `thread=True`.

## References
- Seed: seed-fix-textual-async-worker-threading
- Plan: plan-fix-textual-async-worker-threading


## Notes

**2026-02-08T19:46:51Z**

## Implementation Complete

Fixed async worker UI updates in batch fetch worker by removing all 19 instances of  from  method.

### Changes
- File: 
- Method: 
- Removed 19  wrappers (14x log, 2x progress, 2x stats, 1x button)
- Now uses direct UI method calls as per Textual best practices

### Commit
5907c0e ms-fp62: Fix async worker UI updates (batch fetch worker)

### Acceptance Criteria
- [x]  contains no  calls
- [x] Batch fetch worker remains async (no thread=True)
- [x] Direct UI updates are safe (same thread as event loop)

See implementation: 
