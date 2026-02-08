# Research: ms-ekpx - DuckDB SQL Mode for Advanced Queries

## Ticket Summary
Add an optional advanced query mode using DuckDB SQL for read-only queries against a selected table.

## Current State Analysis

### Existing Infrastructure
- **TablePreviewScreen** (`src/mytt_scraper/tui/screens.py`):
  - Already has filter, sort, and groupby panels
  - Uses PolarsQueryExecutor for query execution
  - Supports both in-memory DataFrames and CSV files
  - Has background worker pattern for async operations

- **Query Model** (`src/mytt_scraper/utils/query_model.py`):
  - Backend-agnostic query model
  - `Backend` type already includes `"duckdb"` as a literal option
  - FilterOp, SortDirection, AggFunc enums defined

- **Query Executor** (`src/mytt_scraper/utils/query_executor.py`):
  - Currently only implements PolarsQueryExecutor
  - Factory function `create_executor()` exists but only supports "polars"
  - Has validation, filter, sort, groupby logic

### Implementation Plan

1. **Add DuckDB dependency** to `pyproject.toml`
2. **Create DuckDBQueryExecutor** class:
   - Support in-memory Arrow/Polars tables via `duckdb.sql()`
   - Support CSV files via `duckdb.read_csv()` or `CREATE VIEW`
   - SELECT-only validation using regex/AST check
   - Limit rows in results
3. **Add SQL Mode to TablePreviewScreen**:
   - Toggle switch between "Builder" (current) and "SQL" modes
   - TextArea for SQL input (when in SQL mode)
   - Execute button for SQL queries
   - Status messages for validation errors
4. **Update query_executor.py** factory to support "duckdb" backend

### Key Design Decisions

- **SELECT-only restriction**: Use regex to check query starts with SELECT
- **In-memory tables**: Use DuckDB's ability to query Arrow/Polars directly
- **CSV files**: Create a temporary view or use `read_csv_auto()`
- **UI Toggle**: Switch between current filter UI and SQL input area
- **Security**: Basic regex validation to prevent writes, but this is MVP

### References
- DuckDB Python API: https://duckdb.org/docs/api/python/overview
- DuckDB can query Polars/Arrow directly: `duckdb.sql("SELECT * FROM df")`
- DuckDB CSV reading: `duckdb.read_csv("file.csv")` or SQL `FROM 'file.csv'`
