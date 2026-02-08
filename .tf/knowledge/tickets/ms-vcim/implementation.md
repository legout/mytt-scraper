# Implementation: ms-vcim

## Summary
Added "View Tables" functionality to the Textual TUI, allowing users to preview extracted tables directly in the TUI after a fetch. The viewer supports both in-memory tables (from current session) and integrates with existing fetch workflows.

## Files Changed

### src/mytt_scraper/tui/app.py
- Added `Any` import from `typing`
- Added `TableListScreen` to imports from `.screens`
- Added `tables: reactive[dict[str, Any]]` reactive state for storing in-memory tables
- Added `TableListScreen` to `SCREENS` dictionary as `"table_list"`
- Added table management methods:
  - `set_tables(tables: dict[str, Any])` - Store in-memory tables from fetch operations
  - `get_tables() -> dict[str, Any]` - Get current in-memory tables
  - `clear_tables()` - Clear all stored tables
  - `has_tables() -> bool` - Check if any tables are available

### src/mytt_scraper/tui/screens.py
- Added `TableListScreen` to `__all__` exports
- Updated `MainMenuScreen`:
  - Added "View Tables" button (id="view-tables") to compose layout
  - Button is disabled by default when no tables are available
  - Added `_update_view_tables_button()` method to control button state
  - Updated `_set_buttons_enabled()` to also update view tables button state
  - Added handler for view-tables button press to navigate to TableListScreen
  - Updated `_do_fetch_own_profile()` to extract and store in-memory tables via `scraper.extract_flat_tables()` and `app.set_tables()`
  - Updated `_do_fetch_external_profile()` similarly
- Added new `TableListScreen` class:
  - Lists available tables with row counts
  - Each table shown as a button
  - Clicking a table opens TablePreviewScreen with the data
  - "Back to Main Menu" button for navigation
  - Escape key binding to go back

## Key Decisions

1. **Reactive Tables State**: Used Textual's `reactive` for the tables dictionary to enable automatic UI updates when tables change.

2. **Polars Backend**: Used `backend="polars"` for `extract_flat_tables()` as it's the project's preferred DataFrame library (evident from existing code).

3. **MVP Approach**: Kept the TableListScreen simple - just a list of buttons. The spike recommended this approach.

4. **Integration with Existing Flows**: Modified both `_do_fetch_own_profile` and `_do_fetch_external_profile` to extract tables and store them in app state, ensuring the "View Tables" button becomes enabled after any successful fetch.

5. **Button State Management**: The "View Tables" button is disabled when no tables are available and enabled automatically when tables are stored. This is checked on mount and after each fetch operation.

## Tests Run
- `uv run pytest tests/test_in_memory_tables.py` - All 21 tests passed
- `python -m py_compile` on modified files - Syntax OK

## Verification
To verify the implementation:
1. Run the TUI: `uv run python -m mytt_scraper.tui`
2. Login with credentials
3. Fetch a profile (own or external)
4. The "View Tables" button should become enabled
5. Click "View Tables" to see the list of extracted tables
6. Click a table to view it in the TablePreviewScreen
7. Use Escape or "Back" buttons to navigate
