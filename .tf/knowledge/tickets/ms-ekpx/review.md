# Review: ms-ekpx

## Critical (must fix)

- `src/mytt_scraper/utils/query_executor.py:170-175` - **UnboundLocalError in execute_sql()**: Connection `con` is referenced in `finally` block but may not be defined if `duckdb.connect()` raises an exception before assignment, causing an UnboundLocalError masking the original error. *(reviewer-general)*

- `src/mytt_scraper/utils/query_executor.py:231-240` - **UnboundLocalError in execute_sql_csv()**: Same issue - `con` may not be defined in finally block if connection fails. *(reviewer-general)*

- `src/mytt_scraper/utils/query_executor.py:336` - **SQL Injection in CSV path**: The `csv_path` is directly interpolated into SQL without sanitization: `con.execute(f"CREATE VIEW {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")`. If the path contains a single quote (`'`), it will break the SQL syntax. Use parameterized queries or proper escaping. *(reviewer-second)*

- `src/mytt_scraper/utils/query_executor.py:290-293` - **Exception handler loses error type**: The `except UnsafeQueryError: raise` block is redundant, and wrapping all exceptions in `QueryExecutorError` loses the original exception type that callers might want to handle differently. *(reviewer-second)*

## Major (should fix)

- `src/mytt_scraper/utils/query_executor.py:186` - **SQL injection vulnerability in CSV path**: If `csv_path` contains single quotes, the SQL syntax breaks. Should use parameterized queries or proper escaping. *(reviewer-general)*

- `src/mytt_scraper/utils/query_executor.py:147-151` - **Double LIMIT clause**: Hardcoded 1000 row limit in `limited_sql` wraps user SQL but ignores any LIMIT already present in user's SQL, potentially confusing users who specified a different limit. *(reviewer-general)*

- `src/mytt_scraper/utils/query_executor.py:219-231` - **Regex-based SQL validation is insufficient**: The pattern only checks for unsafe keywords at the start of the query. Users could bypass this with subqueries or CTEs. Consider using DuckDB's EXPLAIN or query parsing to validate instead of regex. *(reviewer-second)*

- `src/mytt_scraper/utils/query_executor.py:259-260` - **Double LIMIT clause inefficiency**: The code wraps user SQL with `SELECT * FROM ({sql}) LIMIT {self.max_rows}`, but if user's SQL already contains a LIMIT, this creates nested queries. *(reviewer-second)*

- `src/mytt_scraper/utils/query_executor.py:257-265` - **Connection not closed on register() failure**: If `con.register()` raises an exception, the connection won't be closed. Move connection creation inside the try block. *(reviewer-second)*

- `src/mytt_scraper/tui/screens.py:1591-1595` - **SQL input has no length limit**: The TextArea accepts arbitrary-length SQL without validation. A large query could cause memory issues or hang the UI. *(reviewer-second)*

## Minor (nice to fix)

- `src/mytt_scraper/utils/query_executor.py:162-164` - **Redundant exception handling**: Catches `UnsafeQueryError` just to re-raise it - could simply remove the except clause for cleaner code. *(reviewer-general)*

- `src/mytt_scraper/tui/screens.py:953` - **Typo in docstring**: `action_apply()` method docstring refers to "filter" but applies to both filter and SQL modes. *(reviewer-general)*

- `src/mytt_scraper/tui/screens.py:885` - **Inconsistent None checking**: `_get_sql_from_ui()` returns `None` for empty SQL but callers check for falsy values inconsistently. *(reviewer-general)*

- `src/mytt_scraper/tui/screens.py:1484-1485` - **Duplicate button handler**: `elif event.button.id == "reset-btn":` appears twice in `on_button_pressed()`. *(reviewer-second)*

- `src/mytt_scraper/utils/query_executor.py:281` - **Inconsistent table name handling**: `execute_sql()` accepts a `table_name` parameter but the SQL example in docstring hardcodes `data`. *(reviewer-second)*

- `src/mytt_scraper/tui/screens.py:1695` - **total_count is 0 for CSV queries**: When querying CSV files, `total_count` is set from `_base_data` which is None for CSV paths. *(reviewer-second)*

## Warnings (follow-up ticket)

- `tests/test_query_executor.py` - **No tests for DuckDBQueryExecutor**: The entire new functionality lacks unit tests. Should add tests for basic SELECT queries, unsafe query detection, CSV file queries, and error handling. *(reviewer-general)*

- `src/mytt_scraper/utils/query_executor.py:77-78` - **Regex validation can be bypassed**: The `_UNSAFE_PATTERN` regex only checks for unsafe keywords at the start. This provides basic protection but could be bypassed with SQL injection techniques (e.g., `SELECT * FROM data; DROP TABLE foo`). Currently acceptable for read-only MVP. *(reviewer-spec, reviewer-second)*

- `src/mytt_scraper/utils/query_executor.py:217` - **Regex validation can reject valid queries**: A query like `/* INSERT comment */ SELECT * FROM data` would be incorrectly rejected. *(reviewer-second)*

- `src/mytt_scraper/tui/screens.py:1651-1680` - **No query timeout**: Long-running SQL queries could hang the UI indefinitely. Consider adding a timeout parameter. *(reviewer-second)*

- `src/mytt_scraper/utils/query_executor.py:1` - **No duckdb import check**: The code imports duckdb inside methods (lazy loading), but there's no check for duckdb being installed. *(reviewer-second)*

## Suggestions (follow-up ticket)

- `src/mytt_scraper/tui/screens.py:1628-1629` - **Add row limit indicator**: Consider adding a visual indicator of the configured row limit in the SQL UI (e.g., "Limit: 500 rows"). *(reviewer-spec)*

- `src/mytt_scraper/tui/screens.py:1577` - **Persist SQL query history**: Consider persisting recently used SQL queries in session storage. *(reviewer-spec)*

- `src/mytt_scraper/utils/query_executor.py:160` - **Multiple table registration**: Consider exposing `table_name` as a configurable UI element for JOINs across multiple tables. *(reviewer-spec)*

- `src/mytt_scraper/tui/screens.py` - **Keyboard shortcut for SQL mode**: Add keyboard shortcut to toggle SQL mode (e.g., 't' key). *(reviewer-general)*

- `src/mytt_scraper/utils/query_executor.py:132` - **Polars direct support**: DuckDB 0.8+ supports Polars directly via `con.register(table_name, data)` - the `to_arrow()` conversion may be unnecessary. *(reviewer-general)*

- `src/mytt_scraper/utils/query_executor.py:260` - **Preserve user's LIMIT**: Check if query already contains a LIMIT clause and respect it if lower than max_rows. *(reviewer-second)*

- `src/mytt_scraper/tui/screens.py:1582-1583` - **Real-time SQL validation**: Add syntax error indication using DuckDB's query parser. *(reviewer-second)*

- `src/mytt_scraper/tui/screens.py:1620-1627` - **Save/Load SQL queries**: Add buttons to save frequently used queries or load from history. *(reviewer-second)*

## Positive Notes

- ✅ All acceptance criteria satisfied (spec audit)
- Clean integration of SQL mode toggle with reactive pattern
- Good separation of concerns between `DuckDBQueryExecutor` and UI code
- Proper use of background workers for SQL execution
- Consistent error handling with custom exception types
- Support for both in-memory (Polars/PyArrow) and CSV data sources
- Comprehensive CSS styling for SQL mode components
- Factory function properly extended to support new backend

## Summary Statistics
- Critical: 4
- Major: 6
- Minor: 6
- Warnings: 5
- Suggestions: 8

## Spec Coverage
All acceptance criteria verified:
- ✅ A text input area for SQL (restricted to SELECT)
- ✅ Prevent non-SELECT statements (basic guard)
- ✅ Execute via DuckDB and display first N rows
- ✅ Works with in-memory (Arrow/Polars) and disk CSV
