# Implementation: ms-lk6f

## Summary
Fixed async worker UI updates in search worker by removing incorrect `call_from_thread` usage.

## Problem
Textual async workers with default `run_worker(..., thread=False)` run on the app event loop thread. Calling `call_from_thread` from within these workers raises RuntimeError because the code is already on the main thread.

## Solution
Replaced `self.app.call_from_thread(self._update_status, ...)` with direct call `self._update_status(...)` in the `_do_search` method.

## Files Changed
- `src/mytt_scraper/tui/screens.py`
  - `SearchScreen._do_search`: Removed 1 `call_from_thread` call (line 646)
  - Changed from `self.app.call_from_thread(self._update_status, f"[red]Search error: {e}[/]")` to `self._update_status(f"[red]Search error: {e}[/]")`

## Key Decisions
- Followed same pattern as linked ticket ms-ytrd (login + profile fetch fixes)
- Kept worker async (did not add `thread=True`)
- Only fixed the search worker as scoped by this ticket

## Quality Checks
- Python syntax verified: OK
- Change localized to single method as required

## Verification
- Direct method call from async worker is safe since it runs on main event loop
- Error status updates will still render correctly in UI
