---
id: ms-inxx
status: closed
deps: [ms-ay95]
links: [ms-t6ic]
created: 2026-02-08T15:57:30Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-function-to-extract-flat-tables
tags: [tf, backlog, component:docs]
---
# Document in-memory flat table extraction usage

## Task

Document how to use the new in-memory table extraction in README/docs, including a short example for each backend (Polars/Pandas/PyArrow).

## Context

The project currently documents CSV outputs and CLI usage. The new feature is primarily for library consumers and should be discoverable with copy/paste examples.

## Acceptance Criteria

- [ ] README (or docs) includes a minimal snippet: login → fetch → extract_flat_tables
- [ ] Documents backend selection and missing-table behavior
- [ ] Mentions that CSV extraction remains available and unchanged

## References

- Seed: seed-add-a-function-to-extract-flat-tables


## Notes

**2026-02-08T16:21:05Z**

Documentation added to README.md

Added 'In-Memory Table Extraction (Library Usage)' section covering:
- Quick-start snippet (login → fetch → extract_flat_tables)
- Backend selection examples (Polars, Pandas, PyArrow)
- Available tables reference
- Missing table behavior documentation
- Note that CSV extraction remains unchanged

Commit: 293ec68
Review: 0 critical, 0 major, 1 minor, 2 suggestions
