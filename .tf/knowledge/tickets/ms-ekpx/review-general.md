# Review: ms-ekpx

## Overall Assessment
The implementation adds DuckDB SQL mode functionality with a toggle between Builder and SQL interfaces. The code is generally well-structured and follows existing patterns, but has several issues ranging from regex bypass vulnerabilities to error handling gaps and missing tests.

## Critical (must fix)
- `src/mytt_scraper/utils/query_executor.py:170-175` - The regex validation for unsafe SQL can be bypassed with techniques like `/**/INSERT/**/` (comments splitting keywords) or `SELECT 1; DROP TABLE data;` (statement concatenation). The current pattern only checks the start of the string.

- `src/mytt_scraper/utils/query_executor.py:183-195` - Connection `con` is referenced in `finally` block but may not be defined if `duckdb.connect()` raises an exception before assignment, causing an UnboundLocalError masking the original error.

- `src/mytt_scraper/utils/query_executor.py:231-240` - Same UnboundLocalError issue for `execute_sql_csv()` - `con` may not be defined in finally block.

## Major (should fix)
- `src/mytt_scraper/utils/query_executor.py:186` - SQL injection vulnerability in CSV path: `f"CREATE VIEW {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')"` - If `csv_path` contains single quotes, the SQL syntax breaks. Should use parameterized queries or proper escaping.

- `src/mytt_scraper/utils/query_executor.py:147-151` - Hardcoded 1000 row limit in `limited_sql` conflicts with the `self.max_rows` parameter but ignores any LIMIT already present in user's SQL, potentially confusing users who specified a different limit.

- `src/mytt_scraper/tui/screens.py:1047-1048` - Missing `else` branch in `action_apply()` - when not in SQL mode, it calls `self._apply_query()` which doesn't check if `_base_data` is loaded, potentially causing errors if user presses 'a' before data loads.

- `src/mytt_scraper/tui/screens.py:970-975` - `_reset_sql_query()` calls `self._reset_query()` which will try to populate the table with `_base_data`, but if the original data source was a CSV file and user never loaded it into memory, this may fail.

## Minor (nice to fix)
- `src/mytt_scraper/utils/query_executor.py:162-164` - Exception handling catches `UnsafeQueryError` just to re-raise it, which is redundant - could simply remove the except clause for cleaner code.

- `src/mytt_scraper/tui/screens.py:953` - Typo in `action_apply()` method docstring refers to "filter" but applies to both filter and SQL modes.

- `src/mytt_scraper/tui/screens.py:885` - `_get_sql_from_ui()` returns `None` for empty SQL but callers check for falsy values inconsistently - should standardize on empty string or None.

- `src/mytt_scraper/tui/app.py` - CSS for `#sql-controls` is missing `display: none` initial state, relying on Textual's default behavior which may cause brief flash of SQL controls on mount before `watch_sql_mode` runs.

## Warnings (follow-up ticket)
- `tests/test_query_executor.py` - No tests for `DuckDBQueryExecutor` class - the entire new functionality lacks unit tests. Should add tests for:
  - Basic SELECT queries
  - Unsafe query detection/rejection
  - CSV file queries
  - Error handling

- `src/mytt_scraper/utils/query_executor.py` - Consider adding connection pooling or reusing connections for better performance with multiple queries.

## Suggestions (follow-up ticket)
- `src/mytt_scraper/utils/query_executor.py` - Consider using DuckDB's built-in query parsing instead of regex for validation (e.g., `EXPLAIN` the query first to verify it's valid and read-only).

- `src/mytt_scraper/tui/screens.py` - Add keyboard shortcut to toggle SQL mode (e.g., 't' key) for better UX.

- `src/mytt_scraper/tui/screens.py` - Consider persisting SQL query history so users can recall previous queries.

- `src/mytt_scraper/utils/query_executor.py:132` - The `to_arrow()` conversion for Polars DataFrames may be unnecessary since DuckDB 0.8+ supports Polars directly via `con.register(table_name, data)`.

## Positive Notes
- Clean integration of SQL mode toggle with reactive pattern - follows Textual conventions well
- Good separation of concerns between `DuckDBQueryExecutor` and UI code
- Proper use of background workers (`run_worker`) for SQL execution to keep UI responsive
- Consistent error handling with custom exception types (`UnsafeQueryError`, `ValidationError`)
- The CSS styling for SQL mode components is comprehensive and consistent with existing UI
- Factory function `create_executor()` properly extended to support new backend

## Summary Statistics
- Critical: 3
- Major: 4
- Minor: 4
- Warnings: 2
- Suggestions: 4
