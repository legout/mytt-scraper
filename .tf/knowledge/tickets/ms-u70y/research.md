# Research: ms-u70y

## Status
Research enabled. Minimal research performed - this is a design task for internal data structures.

## Context Reviewed
- `tk show ms-u70y` - Ticket requires query model for table viewer
- Existing codebase structure:
  - `src/mytt_scraper/utils/in_memory_tables.py` - Table extraction with Polars/Pandas/PyArrow backends
  - `src/mytt_scraper/tui/screens.py` - TUI screens with DataTable widget
  - `pyproject.toml` - Has polars, pandas, pyarrow, duckdb dependencies

## Design Requirements
1. **Filters**: column, operator, value
2. **Sort**: column, direction (asc/desc)
3. **GroupBy + Aggregations**: column(s), agg functions (sum, count, avg, min, max)
4. **Schema validation**: Validate against column names and types
5. **Backend-agnostic**: Polars executor first, DuckDB optionally later

## References
- Polars API: https://docs.pola.rs/
- DuckDB Python API: https://duckdb.org/docs/api/python/overview

## Sources
- (none - internal design task)
