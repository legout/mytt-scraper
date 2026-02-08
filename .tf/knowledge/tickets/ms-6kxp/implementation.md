# Implementation: ms-6kxp

## Summary
Implemented the SearchScreen with full player search functionality including API/Playwright toggle, results table with selection, and fetch capability.

## Files Changed

### src/mytt_scraper/tui/screens.py
- Added imports for `Switch` and `Checkbox` widgets
- Replaced placeholder `SearchScreen` class with full implementation:
  - Search mode toggle (API vs Playwright via Switch widget)
  - Search input with validation
  - Background worker for non-blocking search
  - Results displayed in DataTable with columns: Name, Club, TTR, User ID
  - Row selection exposes user-id
  - Fetch button to fetch selected player's profile
  - Keyboard shortcuts: Enter to select/fetch, 'f' for fetch, Escape to go back
  - Handles worker state changes for both search and fetch operations

### src/mytt_scraper/tui/app.py
- Updated search container width from 60 to 100 for better table display
- Added CSS styles for new SearchScreen elements:
  - `#search-options`: Layout for toggle and mode indicator
  - `#results-table`: Styling for DataTable with focus state
  - `#selection-bar`: Layout for selection info and fetch button

## Key Design Decisions

1. **Search Mode Toggle**: Uses Switch widget for API/Playwright selection with visual indicator
2. **Results Table**: DataTable with row cursor type allows keyboard navigation and selection
3. **Background Workers**: Search runs in background to keep UI responsive during network calls
4. **Worker Reuse**: Combined worker state handler for both search and fetch workers
5. **Selection Persistence**: Selected user_id stored in instance variable for fetch operation

## Acceptance Criteria Verification

- [x] User can enter a query and trigger search
- [x] Search uses API by default and can switch to Playwright mode
- [x] Results are shown in a list with key fields (name, club, ttr, user-id)
- [x] Selecting a row exposes the user-id for subsequent fetch

## Tests Run
- Syntax check: `python -m py_compile` passed for both files
- Import check: `uv run python -c "from mytt_scraper.tui.screens import SearchScreen"` passed

## Verification
To verify the implementation:
1. Run `uv run python -m mytt_scraper.tui` to start the TUI
2. Login with credentials
3. Select "Search Players" from main menu
4. Enter a player name and click Search (or press Enter)
5. Toggle Playwright mode with the switch
6. Select a row in the results table
7. Click "Fetch Selected" to fetch the profile
