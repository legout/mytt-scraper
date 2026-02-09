---
id: ms-u70y
status: closed
deps: []
links: [ms-0824]
created: 2026-02-08T17:14:57Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-filters-and-advanced-queries-to-the
tags: [tf, backlog, component:query, component:viewer]
---
# Design query model for table viewer (filters/sort/groupby)

## Task

Define a small internal query model for the table viewer: filters, sort, and aggregation operations that can be executed via Polars (MVP) and optionally DuckDB later.

## Context

We want interactive filtering and aggregation in the Textual TUI for both in-memory and disk-backed tables.

## Acceptance Criteria

- [ ] Define data structures for:
  - filters (column, op, value)
  - sort (column, direction)
  - groupby + aggregations
- [ ] Model supports validation against a table schema (column names/types)
- [ ] Query model is backend-agnostic (Polars executor first)

## References

- Seed: seed-add-filters-and-advanced-queries-to-the
- Related: seed-add-table-viewer-to-the-tui


## Notes

**2026-02-08T17:55:34Z**

Implemented query model for table viewer with filters, sort, and groupby operations.

## Summary

- Created query model data structures (Filter, Sort, GroupBy, Aggregation, Query, TableSchema)
- Implemented PolarsQueryExecutor with lazy evaluation
- Added comprehensive tests (81 new tests, all passing)
- Supports schema validation and backend-agnostic design

## Files Added
- src/mytt_scraper/utils/query_model.py
- src/mytt_scraper/utils/query_executor.py
- tests/test_query_model.py
- tests/test_query_executor.py

## Files Modified
- src/mytt_scraper/utils/__init__.py (exports)

## Verification
- All 104 tests pass
- Implementation meets all acceptance criteria

Commit: 4e4a323
