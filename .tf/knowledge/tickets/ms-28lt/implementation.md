# Implementation: ms-28lt

## Summary
Implemented MainMenuScreen with full functionality for fetching own profile and fetching external profiles by user ID, following the existing LoginScreen patterns with background workers.

## Files Changed

### `src/mytt_scraper/tui/screens.py`
**Major changes:**
1. **Updated imports**: Added `Path`, `Horizontal`, `ModalScreen`, and `DataTable` imports
2. **Extended `__all__`**: Added `UserIdInputScreen` and `ResultScreen`
3. **Rewrote `MainMenuScreen`**:
   - Added background worker support (`_fetch_worker`)
   - Added status display (`#menu-status` Static widget)
   - Implemented `_start_fetch_own_profile()` with background worker
   - Implemented `_do_fetch_own_profile()` async worker method
   - Implemented `_show_user_id_input()` with modal callback
   - Implemented `_do_fetch_external_profile()` async worker method
   - Added `_get_tables_written()` to list CSV files in tables directory
   - Added worker state change handler for success/failure/cancelled states
   - Added `_handle_fetch_success()` and `_handle_fetch_failure()` methods
   - Added `_set_buttons_enabled()` to disable/enable UI during operations

4. **Added `UserIdInputScreen`** (new ModalScreen):
   - Input field for user ID
   - Cancel and Fetch buttons
   - Returns user ID string or None (if cancelled)
   - Escape key binding to cancel

5. **Added `ResultScreen`** (new ModalScreen):
   - Shows success message with profile type
   - Displays tables directory path
   - Lists files written (up to 10, with "...and N more" indicator)
   - Close button and escape key binding

### `src/mytt_scraper/tui/app.py`
**Changes:**
1. **Updated imports**: Added `UserIdInputScreen` and `ResultScreen`
2. **Extended `SCREENS` dict**: Added entries for `user_id_input` and `result`
3. **Updated CSS**: Added styles for:
   - `#menu-status` - status display in main menu
   - `#userid-dialog` and `#result-dialog` - modal dialog containers
   - `#userid-title` and `#result-title` - modal titles
   - `#userid-buttons` - button container for user ID input
   - `Screen` alignment fix for modal positioning

## Key Design Decisions

1. **Background Worker Pattern**: Following LoginScreen's pattern, all fetch operations run in background workers to keep the UI responsive. Status updates use `call_from_thread()` for thread safety.

2. **Modal Screens for User Input**: User ID input uses a modal dialog (`UserIdInputScreen`) that dismisses with the entered value or None, allowing the main menu to handle the result asynchronously.

3. **Result Summary**: After successful fetch, a `ResultScreen` modal shows what was fetched and which CSV files were written to the tables directory.

4. **Button State Management**: During operations, all menu buttons are disabled to prevent concurrent operations. They're re-enabled on completion or error.

5. **Error Handling**: Failed operations show error notifications and re-enable the UI for retry.

## Acceptance Criteria Coverage

- [x] Main menu lists actions and routes to the right handler
  - "Fetch My Profile" → `_start_fetch_own_profile()`
  - "Search Players" → pushes SearchScreen
  - "Fetch by User ID" → `_show_user_id_input()` → modal → fetch

- [x] Fetch own profile runs and reports success/failure
  - Background worker runs `scraper.run_own_profile()`
  - Success shows ResultScreen with summary
  - Failure shows error notification

- [x] Fetch external profile prompts for user-id and runs
  - UserIdInputScreen modal prompts for input
  - Background worker runs `scraper.run_external_profile(user_id)`

- [x] After each action, show a short summary
  - ResultScreen shows: success message, tables directory, files written

## Tests Run
- Syntax validation: `python -m py_compile` passed
- Import test: `from mytt_scraper.tui.screens import MainMenuScreen, UserIdInputScreen, ResultScreen` passed
- Import test: `from mytt_scraper.tui.app import MyttScraperApp` passed

## Verification
Run the TUI with: `python -m mytt_scraper.tui` (requires valid credentials)
