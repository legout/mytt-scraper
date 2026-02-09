---
id: ms-f9r5
status: closed
deps: [ms-ekpx]
links: [ms-ekpx]
created: 2026-02-08T17:14:58Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-filters-and-advanced-queries-to-the
tags: [tf, backlog, component:docs, component:query, component:tui]
---
# Document filters/queries usage and limitations

## Task

Document how to use filters, sorting, and aggregations in the TUI table viewer, including limits (row cap, supported operators).

## Acceptance Criteria

- [ ] Docs include examples for filter/sort/groupby
- [ ] Docs mention row cap and lazy evaluation rationale
- [ ] Docs mention Polars backend (and DuckDB if enabled)

## References

- Seed: seed-add-filters-and-advanced-queries-to-the


## Notes

**2026-02-08T18:19:45Z**

Documentation complete. Created docs/TUI_TABLE_QUERIES.md with comprehensive guide for filters, sorting, aggregations, and SQL queries in the TUI table viewer.

Includes:
- Filter examples for all operators (=, ≠, >, ≥, <, ≤, contains)
- Sort and groupby examples with all aggregations
- Row cap (500) and lazy evaluation rationale
- Polars backend and DuckDB SQL mode documentation
- Keyboard shortcuts and common use cases

Commit: ad04f5f
