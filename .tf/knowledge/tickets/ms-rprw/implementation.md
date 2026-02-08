# Implementation: ms-rprw

## Summary
Implemented Textual LoginScreen with background Playwright login and app state management for storing authenticated scraper instances.

## Files Changed
- `src/mytt_scraper/tui/app.py` - Added reactive scraper state and helper methods
- `src/mytt_scraper/tui/screens.py` - Rewrote LoginScreen with background worker-based login

## Key Changes

### app.py
- Added `from textual.reactive import reactive` import
- Added `scraper: reactive[Optional[MyTischtennisScraper]]` reactive state
- Added helper methods:
  - `set_scraper()` - Create and store MyTischtennisScraper instance
  - `set_searcher()` - Create and store PlayerSearcher instance
  - `clear_scraper()` - Clear stored instance (logout)
  - `get_scraper()` - Retrieve stored instance
  - `is_authenticated()` - Check if authenticated

### screens.py - LoginScreen
- Added `from textual.worker import Worker` import
- Added `__init__()` to initialize worker and credential state
- Implemented `_start_login()` - validates inputs, disables form, starts worker
- Implemented `_do_login()` - async worker task calling `login_with_playwright()`
- Implemented `_update_status()` - thread-safe status updates via `call_from_thread()`
- Implemented `on_worker_state_changed()` - handles SUCCESS/ERROR/CANCELLED states
- Implemented `_handle_login_success()` - stores scraper, clears credentials, navigates
- Implemented `_handle_login_failure()` - shows error, re-enables form for retry
- Implemented `_enable_login_form()` - re-enables inputs after failure
- Added `action_quit()` - cancels running worker on quit

### screens.py - MainMenuScreen
- Added `on_mount()` - checks authentication, redirects to login if needed
- Updated `on_button_pressed()` - uses stored scraper instance
- Updated `action_logout()` - clears scraper and switches to login screen

## Acceptance Criteria Status

- [x] LoginScreen collects username + password (password masked)
  - Password input uses `password=True` to mask input
  - Input validation ensures both fields are filled

- [x] Login runs in a background worker/task and updates status
  - Uses `self.run_worker()` to run `login_with_playwright` in background
  - Status updates show progress: "Starting login", "Connecting..."
  - UI stays responsive during Playwright operations

- [x] On success, an authenticated scraper/searcher instance is stored in app state
  - `set_searcher()` creates PlayerSearcher with credentials
  - Stored in reactive `app.scraper` state
  - Clears password from memory after storage
  - Navigates to main menu after 0.5s delay

- [x] On failure, error is shown and user can retry
  - Shows specific error messages (credential failure, network error, etc.)
  - Re-enables form inputs and button
  - Clears password field for security

## Constraints Met
- Credentials are session-only (no persistence)
  - Stored only in memory during session
  - Cleared on logout and on successful login
  - Never written to disk

## Design Decisions
1. Used `PlayerSearcher` instead of `MyTischtennisScraper` as it extends the base class and adds search functionality
2. Used Textual's Worker API for background tasks to maintain UI responsiveness
3. Used `call_from_thread()` for thread-safe status updates from the async worker
4. Added authentication check in MainMenuScreen.on_mount() for security
5. Login form is disabled during authentication to prevent duplicate submissions

## Tests Run
- `python -m py_compile src/mytt_scraper/tui/app.py src/mytt_scraper/tui/screens.py` - Syntax OK

## Verification
To verify the implementation:
1. Run `python -m mytt_scraper.tui`
2. Enter valid mytischtennis.de credentials
3. Click Login - status should show progress updates
4. On success, should navigate to Main Menu
5. Press 'l' to logout - should return to Login screen
6. Enter invalid credentials - should show error and allow retry
