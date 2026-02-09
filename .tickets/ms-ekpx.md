---
id: ms-ekpx
status: closed
deps: [ms-b2hw]
links: [ms-b2hw, ms-f9r5]
created: 2026-02-08T17:14:58Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-filters-and-advanced-queries-to-the
tags: [tf, backlog, component:duckdb, component:query, component:viewer]
---
# Optional: DuckDB SQL mode for advanced queries (read-only)

## Task

Add an optional advanced query mode using DuckDB SQL for read-only queries against a selected table.

## Context

Some users prefer SQL. DuckDB can query CSVs and Arrow/Polars data efficiently.

## Acceptance Criteria

- [ ] A text input area for SQL (restricted to SELECT)
- [ ] Prevent non-SELECT statements (basic guard)
- [ ] Execute via DuckDB and display first N rows
- [ ] Works with in-memory (Arrow/Polars) and disk CSV

## Constraints

- MVP can skip implementing this if scope is too large

## References

- Seed: seed-add-filters-and-advanced-queries-to-the


## Notes

**2026-02-08T18:16:50Z**

Implemented DuckDB SQL mode for advanced queries in TUI.

Changes:
- Added DuckDBQueryExecutor class with SELECT-only validation
- Added SQL mode toggle to TablePreviewScreen
- SQL input area with syntax highlighting
- Works with both in-memory (Polars/PyArrow) and CSV files
- Basic SQL injection protection for CSV paths

Commit: 0bf8966
