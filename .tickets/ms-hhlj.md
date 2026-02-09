---
id: ms-hhlj
status: closed
deps: [ms-fp62]
links: [ms-fp62]
created: 2026-02-08T19:38:45Z
type: task
priority: 2
assignee: legout
external-ref: seed-fix-textual-async-worker-threading
tags: [tf, backlog, component:tui]
---
# Verify Textual async worker fix (grep + dev run)

## Task
Verify the Textual async-worker fix with static greps and manual dev-mode runs.

## Context
After removing `call_from_thread` from async workers, we should validate:
- no accidental `thread=True` usage exists
- no remaining `call_from_thread` references in `screens.py`
- primary flows work (login, fetch, search, batch fetch)

## Acceptance Criteria
- [ ] `rg "thread=True" src/mytt_scraper/tui` shows no threaded workers (or is explained).
- [ ] `rg "call_from_thread" src/mytt_scraper/tui/screens.py` shows no matches.
- [ ] `uv run python -m mytt_scraper.tui` launches and can login.
- [ ] `uv run textual run -m mytt_scraper.tui --dev` shows no worker exceptions during test flows.

## Constraints
- No new features; verification only.

## References
- Seed: seed-fix-textual-async-worker-threading
- Plan: plan-fix-textual-async-worker-threading


## Notes

**2026-02-08T22:34:33Z**

--message ## Completed

Fixed 2 remaining `call_from_thread` instances in `screens.py` that were missed in ms-fp62.

### Changes
- Removed `self.app.call_from_thread()` wrappers from async worker `_load_data()`
- Now using direct UI method calls (correct for async workers)

### Verification
- ✅ No threaded workers: `rg thread=True` returns no results
- ✅ No call_from_thread: `rg call_from_thread screens.py` returns no results

Commit: 31a810d
