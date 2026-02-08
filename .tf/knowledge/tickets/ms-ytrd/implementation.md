# Implementation: ms-ytrd

## Summary
Fix async worker UI updates by removing incorrect `call_from_thread` usage in login and profile fetch flows.

## Problem
Textual async workers (default `run_worker(..., thread=False)`) run on the app event loop thread. Calling `call_from_thread` from within these workers raises a RuntimeError because the code is already on the main thread, not in a separate thread.

## Solution
Replace `self.app.call_from_thread(self._update_status, ...)` with direct calls to `self._update_status(...)` since:
1. Async workers run on the main event loop thread
2. UI updates from the main thread can be called directly
3. `call_from_thread` is only needed when calling from a background thread

## Files Changed
- `src/mytt_scraper/tui/screens.py`
  - `LoginScreen._do_login`: Removed 2 `call_from_thread` calls
  - `MainMenuScreen._do_fetch_own_profile`: Removed 4 `call_from_thread` calls
  - `MainMenuScreen._do_fetch_external_profile`: Removed 4 `call_from_thread` calls

## Verification
- `uv run python -m mytt_scraper.tui` can login without crashing
- Profile fetch operations update status correctly
