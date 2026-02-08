# Review: ms-ytrd

## Critical (must fix)
(none)

## Major (should fix)
(none)

## Minor (nice to fix)
(none)

## Warnings (follow-up ticket)
1. **SearchScreen._do_search still has call_from_thread** (line ~548)
   - `self.app.call_from_thread(self._update_status, ...)` in the exception handler
   - This will crash if an exception occurs during search
   - Tracked in linked ticket ms-lk6f

2. **BatchFetchScreen._do_batch_fetch has many call_from_thread calls**
   - Multiple `call_from_thread` usages for `_log_message`, `_update_progress`, `_update_stats`
   - This will also crash the batch fetch feature
   - May need separate ticket if not covered by ms-lk6f

3. **TablePreviewScreen._load_data has call_from_thread**
   - Uses `call_from_thread` for `_update_status` calls
   - Will crash when loading table previews

## Summary Statistics
- Critical: 0
- Major: 0
- Minor: 0
- Warnings: 3
- Suggestions: 0

## Notes
The main fix for login and profile fetch flows is correct. All `call_from_thread` calls have been replaced with direct method calls in:
- `LoginScreen._do_login` (2 instances)
- `MainMenuScreen._do_fetch_own_profile` (4 instances)
- `MainMenuScreen._do_fetch_external_profile` (4 instances)

The remaining warnings are in other screens that also need fixing but are tracked separately or may need follow-up tickets.
