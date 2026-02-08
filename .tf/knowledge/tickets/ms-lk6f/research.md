# Research: ms-lk6f

## Status
Research enabled. No additional external research needed - pattern established by linked ticket ms-ytrd.

## Context from ms-ytrd
Async workers with `run_worker(..., thread=False)` run on the app event loop thread. Calling `call_from_thread` from these workers raises RuntimeError since the code is already on the main thread. Solution is direct method calls.

## Files to Modify
- `src/mytt_scraper/tui/screens.py` - `_do_search` method (line 646)

## Pattern to Apply
Replace `self.app.call_from_thread(self._update_status, ...)` with direct `self._update_status(...)` call.

## Sources
- Ticket ms-ytrd implementation (same fix pattern)
- Textual docs: async workers run on main event loop
