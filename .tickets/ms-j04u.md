---
id: ms-j04u
status: closed
deps: [ms-861m]
links: [ms-861m, ms-xj1i]
created: 2026-02-08T19:24:57Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-comprehensive-documentation-using-th
tags: [tf, backlog, docs, component:docs, component:api]
---
# Write reference: Python API (REPL usage) including in-memory tables

## Task

Create a Python API reference with REPL/notebook examples, including in-memory table extraction and disk fallback loading.

## Acceptance Criteria

- [ ] Create `docs/reference/python-api.md`
- [ ] Documents `MyTischtennisScraper` and `PlayerSearcher`
- [ ] Documents `extract_flat_tables` (if implemented) and expected return shape
- [ ] Shows Polars/DuckDB examples:
  - load from in-memory DataFrame
  - load from disk (CSV) using Polars or DuckDB

## References

- Plan: plan-diataxis-documentation-cli-repl-tui


## Notes

**2026-02-08T23:27:10Z**

Implemented Python API reference documentation.

## Summary
- Created docs/reference/python-api.md with comprehensive API documentation
- Documents MyTischtennisScraper (all public methods)
- Documents PlayerSearcher (search methods and interactive modes)
- Documents extract_flat_tables with return shape and backend options
- Includes 4 workflow examples: direct analysis, Polars in-memory, Polars from disk, DuckDB from disk
- Updated docs/reference/index.md to include Python API link

## Changes
- docs/reference/python-api.md (new)
- docs/reference/index.md (updated)

## Commit
e9a6ba4 ms-j04u: Add Python API reference documentation

## Review
- 1 major issue fixed: Corrected Optional return types for fetch methods
- All acceptance criteria met
