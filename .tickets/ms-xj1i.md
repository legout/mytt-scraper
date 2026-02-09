---
id: ms-xj1i
status: closed
deps: [ms-j04u]
links: [ms-j04u, ms-btdf]
created: 2026-02-08T19:24:57Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-comprehensive-documentation-using-th
tags: [tf, backlog, docs, component:docs, component:explanation]
---
# Write explanation: architecture + in-memory vs disk tables

## Task

Write explanation pages for system architecture and table data strategy.

## Acceptance Criteria

- [ ] Create `docs/explanation/architecture.md` (Playwright login → cookies → requests → extraction)
- [ ] Create `docs/explanation/in-memory-vs-disk-tables.md` (why in-memory first; CSV fallback; Polars/DuckDB)
- [ ] Cross-link to relevant reference/how-to pages

## References

- Plan: plan-diataxis-documentation-cli-repl-tui


## Notes

**2026-02-08T23:29:40Z**

Implemented explanation documentation:

- Created docs/explanation/architecture.md with system architecture overview covering Playwright login → cookies → requests → extraction pipeline
- Created docs/explanation/in-memory-vs-disk-tables.md explaining in-memory first philosophy, CSV fallback, and Polars/DuckDB usage
- Updated docs/explanation/index.md to list new documents
- Cross-linked to relevant reference/how-to pages throughout

Commit: 03a46e5
