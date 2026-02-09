---
id: ms-b7cc
status: closed
deps: [ms-fkf4]
links: [ms-fkf4, ms-24n1]
created: 2026-02-08T16:50:56Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-table-viewer-to-the-tui
tags: [tf, backlog, component:viewer, component:tui]
---
# Build TablePreviewScreen using Textual DataTable + Polars/PyArrow

## Task

Implement `TablePreviewScreen` that renders a selected table preview using `textual.widgets.DataTable`, with data loaded via Polars/PyArrow/DuckDB.

## Context

The viewer should support both in-memory tables (Polars DataFrames) and disk-based tables (CSV). Using Polars/PyArrow provides:
- Fast CSV parsing with automatic type inference
- Lazy evaluation (`.head(N)`) to avoid loading full files
- DuckDB integration for SQL-like filtering

## Acceptance Criteria

- [ ] Accept a `TableProvider` (in-memory or disk source)
- [ ] Load data using Polars (`pl.read_csv().head(N)`) or use existing DataFrame if in-memory
- [ ] Create DataTable with column headers from Polars schema
- [ ] Populate DataTable with first N rows (configurable, default 200)
- [ ] Support navigation back to the table list
- [ ] Wide tables: allow horizontal scroll; optional column selection mode
- [ ] Show row count (e.g., "Showing 200 of 1,500 rows")

## Constraints

- Must use lazy loading (`.head()`) to avoid loading entire files into memory
- Must work with both Polars DataFrame and PyArrow Table inputs

## References

- Seed: seed-add-table-viewer-to-the-tui
- Spike: spike-table-viewer-for-python-tui-textual (DataTable capabilities)
- Related: seed-add-a-function-to-extract-flat-tables (Polars/PyArrow extraction)

## Blockers

- ms-fkf4 [open] Implement table discovery (in-memory + disk) with friendly names

## Blocking

- ms-24n1 [open] Load data in background worker for responsive table viewing

## Linked

- ms-fkf4 [open] Implement table discovery (in-memory + disk) with friendly names
- ms-24n1 [open] Load data in background worker for responsive table viewing

## Notes

**2026-02-08T18:46:21Z**

## Implementation Complete

### Changes Made
- Modified  to accept  for unified table access
- Implemented lazy loading using  for disk-based tables
- Changed default limit from 500 to 200 rows for better performance
- Updated  to pass  directly
- Added proper row count display: 'Showing X of Y rows' format

### Verification
- All 104 tests pass
- Syntax check passed
- Commit: 047dd67

### Artifacts
-  - Implementation details
-  - Review results (no issues found)
-  - Fixes applied (none required)
