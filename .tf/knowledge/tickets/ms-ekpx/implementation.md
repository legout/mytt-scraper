# Implementation: ms-ekpx - DuckDB SQL Mode for Advanced Queries

## Summary
Added an optional advanced query mode using DuckDB SQL for read-only queries against tables in the TUI.

## Files Changed

### 1. `src/mytt_scraper/utils/query_executor.py`
- Added `UnsafeQueryError` exception class for non-SELECT queries
- Added `DuckDBQueryExecutor` class with:
  - `_validate_select_only()`: Regex-based validation to ensure only SELECT queries
  - `execute_sql()`: Execute SQL against in-memory Polars/PyArrow data
  - `execute_sql_csv()`: Execute SQL against CSV files
  - Configurable `max_rows` limit for safety
- Updated `create_executor()` factory to support "duckdb" backend

### 2. `src/mytt_scraper/tui/screens.py`
- Added imports for `TextArea`, `reactive`, `DuckDBQueryExecutor`, `UnsafeQueryError`
- Added `sql_mode: reactive[bool]` to `TablePreviewScreen`
- Updated `compose()` to add:
  - Mode toggle switch (Builder/SQL)
  - SQL input container with `TextArea` for SQL queries
  - SQL action buttons (Run SQL, Reset SQL)
- Added methods:
  - `watch_sql_mode()`: Toggle visibility between builder and SQL controls
  - `on_switch_changed()`: Handle SQL mode toggle
  - `_get_sql_from_ui()`: Get SQL from text area
  - `_run_sql_query()`: Execute SQL query
  - `_do_sql_query()`: Background worker for SQL execution
  - `_reset_sql_query()`: Reset SQL to default
- Updated `on_button_pressed()` to handle SQL buttons
- Updated `on_worker_state_changed()` to handle `sql_query_worker` results

### 3. `src/mytt_scraper/tui/app.py`
- Added CSS styles for SQL mode UI components:
  - `#query-mode-toggle`
  - `#mode-label`
  - `#sql-input-container`
  - `#sql-input`
  - `#sql-actions`

## Key Decisions

1. **SELECT-only restriction**: Uses regex pattern matching to reject queries starting with unsafe keywords (INSERT, UPDATE, DELETE, DROP, etc.)

2. **In-memory data support**: DuckDB can query Polars/PyArrow data directly via `con.register()`

3. **CSV file support**: Uses DuckDB's `read_csv_auto()` function for CSV files

4. **Row limits**: Both executor and SQL queries have configurable row limits for safety

5. **UI Toggle**: Simple switch between Builder (existing filter UI) and SQL mode

## Acceptance Criteria Status

- [x] A text input area for SQL (restricted to SELECT) - Implemented via `TextArea`
- [x] Prevent non-SELECT statements (basic guard) - Implemented via regex validation
- [x] Execute via DuckDB and display first N rows - Implemented in `DuckDBQueryExecutor`
- [x] Works with in-memory (Arrow/Polars) and disk CSV - Both paths implemented

## Tests Run

- Python syntax check passed for all modified files
- Files compile without errors

## Verification

To verify the implementation:
1. Run the TUI: `uv run python -m mytt_scraper.tui`
2. Login and fetch data
3. Open a table preview
4. Toggle "Mode" switch to "SQL"
5. Enter a SELECT query (e.g., `SELECT * FROM data LIMIT 50`)
6. Click "Run SQL"
7. Results should display in the table
