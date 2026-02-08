# Review (Spec Audit): ms-ekpx

## Overall Assessment
The implementation fully satisfies all acceptance criteria for the DuckDB SQL mode feature. The SQL input area, SELECT-only restriction, DuckDB execution with row limits, and support for both in-memory (Arrow/Polars) and CSV data sources are all correctly implemented in the TUI.

## Critical (must fix)
No issues found.

## Major (should fix)
No issues found.

## Minor (nice to fix)
No issues found.

## Warnings (follow-up ticket)
- `src/mytt_scraper/utils/query_executor.py:77-78` - The `_UNSAFE_PATTERN` regex only checks for unsafe keywords at the start of the query. This provides basic protection but could be bypassed with SQL injection techniques (e.g., `SELECT * FROM data; DROP TABLE foo`). Consider a more robust parsing approach for production use if this becomes a security concern. Currently acceptable for read-only MVP as specified.

## Suggestions (follow-up ticket)
- `src/mytt_scraper/tui/screens.py:1628-1629` - Consider adding a visual indicator of the configured row limit in the SQL UI (e.g., "Limit: 500 rows") to inform users why large result sets are truncated.
- `src/mytt_scraper/tui/screens.py:1577` - Consider persisting recently used SQL queries in session storage for user convenience.
- `src/mytt_scraper/utils/query_executor.py:160` - Consider exposing `table_name` as a configurable UI element so users can reference multiple registered tables in joins (future enhancement).

## Positive Notes
- ✅ **SELECT-only restriction**: `DuckDBQueryExecutor._validate_select_only()` correctly implements regex-based validation to reject INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, and other unsafe keywords at line 77-78
- ✅ **Text input area for SQL**: `TextArea` widget with `language="sql"` properly configured at screens.py line 1540
- ✅ **Execute via DuckDB**: `execute_sql()` and `execute_sql_csv()` methods use DuckDB with configurable `max_rows` limit (lines 97-176)
- ✅ **In-memory data support**: `execute_sql()` handles both Polars DataFrames and PyArrow Tables via `con.register()` at lines 121-128
- ✅ **CSV file support**: `execute_sql_csv()` uses `read_csv_auto()` for CSV querying at lines 149-155
- ✅ **UI Toggle**: Mode switch between Builder and SQL modes implemented via reactive `sql_mode` property and `watch_sql_mode()` method
- ✅ **Background execution**: SQL queries run in `sql_query_worker` to keep UI responsive
- ✅ **Proper error handling**: `UnsafeQueryError`, `ValidationError`, and `QueryExecutorError` exceptions handled with user-friendly messages
- ✅ **CSS styling**: Complete styles for SQL UI components in app.py lines 218-232

## Summary Statistics
- Critical: 0
- Major: 0
- Minor: 0
- Warnings: 1
- Suggestions: 3

## Spec Coverage
- Spec/plan sources consulted:
  - `.tickets/ms-ekpx.md` - Ticket requirements
  - `.tf/knowledge/topics/seed-add-filters-and-advanced-queries-to-the/seed.md` - Seed document
  - `.tickets/ms-b2hw.md` - Linked ticket (sort/groupby - closed)
- Missing specs: None

## Acceptance Criteria Verification

| Criterion | Status | Implementation Location |
|-----------|--------|------------------------|
| A text input area for SQL (restricted to SELECT) | ✅ PASS | `screens.py:1540` (TextArea), `query_executor.py:77-96` (validation) |
| Prevent non-SELECT statements (basic guard) | ✅ PASS | `query_executor.py:77-78` (_UNSAFE_PATTERN regex), lines 86-94 (SELECT prefix check) |
| Execute via DuckDB and display first N rows | ✅ PASS | `query_executor.py:97-176` (execute_sql, execute_sql_csv with LIMIT) |
| Works with in-memory (Arrow/Polars) and disk CSV | ✅ PASS | `query_executor.py:121-128` (Polars/PyArrow), lines 149-155 (CSV) |
