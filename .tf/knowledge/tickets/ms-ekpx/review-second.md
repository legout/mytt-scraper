# Review (Second Opinion): ms-ekpx

## Overall Assessment
The DuckDB SQL mode implementation is functionally complete and follows the existing codebase patterns well. However, there are security concerns with the SQL validation approach and potential SQL injection vulnerabilities that should be addressed. The UI integration is clean and the background worker pattern is properly implemented.

## Critical (must fix)
- `src/mytt_scraper/utils/query_executor.py:336` - **SQL Injection in CSV path**: The `csv_path` is directly interpolated into SQL without sanitization: `con.execute(f"CREATE VIEW {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")`. If the path contains a single quote (`'`), it will break the SQL syntax. Use parameterized queries or proper escaping.

- `src/mytt_scraper/utils/query_executor.py:290-293` - **Exception handler catches UnsafeQueryError and re-raises as generic error**: The `except UnsafeQueryError: raise` block is redundant but also problematic because any exception during SQL execution gets wrapped in `QueryExecutorError`, potentially losing the original exception type that callers might want to handle differently.

## Major (should fix)
- `src/mytt_scraper/utils/query_executor.py:219-231` - **Regex-based SQL validation is insufficient**: The pattern only checks for unsafe keywords at the start of the query. Users could bypass this with subqueries or CTEs: `SELECT * FROM (DROP TABLE data) AS x`. Consider using DuckDB's EXPLAIN or query parsing to validate instead of regex.

- `src/mytt_scraper/utils/query_executor.py:259-260` - **Double LIMIT clause potential issue**: The code wraps user SQL with `SELECT * FROM ({sql}) LIMIT {self.max_rows}`, but if the user's SQL already contains a LIMIT, this creates nested queries with multiple LIMITs. DuckDB handles this, but it's inefficient and could confuse users expecting their LIMIT to be respected.

- `src/mytt_scraper/utils/query_executor.py:257-265` - **Connection not closed on register() failure**: If `con.register()` raises an exception, the connection won't be closed because the `try` block starts after registration. Move connection creation inside the try block or add a separate try/except around registration.

- `src/mytt_scraper/tui/screens.py:1591-1595` - **SQL input has no length limit**: The TextArea accepts arbitrary-length SQL without validation. A malicious or accidental paste of a very large query could cause memory issues or hang the UI.

## Minor (nice to fix)
- `src/mytt_scraper/tui/screens.py:1484-1485` - **Duplicate button handler**: `elif event.button.id == "reset-btn":` appears twice in `on_button_pressed()`. While not causing bugs currently (the second one never executes), this should be cleaned up.

- `src/mytt_scraper/utils/query_executor.py:281` - **Inconsistent table name handling**: `execute_sql()` accepts a `table_name` parameter but the SQL example in docstring hardcodes `data`. The screens.py always uses `table_name="data"`, making the parameter less useful than intended.

- `src/mytt_scraper/tui/screens.py:1695` - **total_count is 0 for CSV queries**: When querying CSV files, `total_count` is set to `len(self._base_data) if self._base_data is not None else 0`, which will always be 0 for CSV paths since `_base_data` is only set when loading in-memory data.

- `src/mytt_scraper/tui/screens.py:1536-1543` - **SQL reset calls `_reset_query()`**: The `_reset_sql_query()` method resets the SQL text but then calls `_reset_query()` which only resets the builder UI state, not the SQL mode display. Consider if this is the intended behavior.

## Warnings (follow-up ticket)
- `src/mytt_scraper/utils/query_executor.py:217` - **Regex validation can reject valid queries**: A query like `/* INSERT comment */ SELECT * FROM data` would be incorrectly rejected because the regex doesn't properly handle comments before removing them. Consider using a proper SQL parser for validation.

- `src/mytt_scraper/tui/screens.py:1651-1680` - **No query timeout for SQL execution**: Long-running SQL queries could hang the UI indefinitely. Consider adding a timeout parameter to DuckDB execution.

- `src/mytt_scraper/utils/query_executor.py:1` - **DuckDB dependency not in imports check**: The code imports duckdb inside methods, which is fine for lazy loading, but there's no check for duckdb being installed. If it's not in the project's required dependencies, users will get import errors at runtime.

## Suggestions (follow-up ticket)
- `src/mytt_scraper/utils/query_executor.py:260` - **Consider preserving user's LIMIT**: Instead of always wrapping with LIMIT, check if the query already contains a LIMIT clause and respect it if it's lower than max_rows.

- `src/mytt_scraper/tui/screens.py:1582-1583` - **Add SQL syntax highlighting validation**: The TextArea has `language="sql"` but could benefit from real-time syntax error indication using DuckDB's query parser.

- `src/mytt_scraper/tui/screens.py:1620-1627` - **Save/Load SQL queries**: Consider adding buttons to save frequently used queries or load from history.

- `src/mytt_scraper/utils/query_executor.py:280` - **Support for multiple table registration**: Currently only supports one table name. Could be extended to allow JOINs across multiple registered DataFrames.

## Positive Notes
- Clean integration of SQL mode toggle with reactive pattern (`sql_mode: reactive[bool]`)
- Good use of background workers for SQL execution to prevent UI blocking
- Proper error handling with specific exception types (`UnsafeQueryError`, `ValidationError`)
- Support for both in-memory (Polars/PyArrow) and CSV file data sources
- Configurable `max_rows` safety limit is a good defensive programming practice
- Consistent with existing builder pattern UI (Apply/Reset buttons)
- The `_validate_select_only()` method includes both keyword and SELECT-start checks for defense in depth
- Good documentation with docstrings and examples in the executor classes

## Summary Statistics
- Critical: 2
- Major: 4
- Minor: 4
- Warnings: 3
- Suggestions: 4
