---
id: ms-24my
status: closed
deps: [ms-24n1]
links: [ms-24n1]
created: 2026-02-08T16:50:56Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-table-viewer-to-the-tui
tags: [tf, backlog, component:docs, component:tui, component:viewer]
---
# Document TUI table viewer usage + data sources (in-memory vs disk)

## Task

Document how to use the table viewer in the Textual TUI, including the dual-source approach (in-memory vs disk), row limits, and performance considerations.

## Context

Users should understand:
- The viewer prioritizes in-memory tables (if fetched in current session)
- Falls back to loading from CSV files using Polars for fast parsing
- Previews are capped for performance

## Acceptance Criteria

- [ ] Docs explain the dual-source behavior (memory first, disk fallback)
- [ ] Docs mention how to open "View Tables" and select a table
- [ ] Docs describe row cap behavior (default 200 rows) and why it exists
- [ ] Docs list supported table types (ttr_rankings, league_table, etc.)
- [ ] Docs mention Polars/PyArrow is used for fast loading
- [ ] Docs explain the indicator showing data source (memory vs disk icon)

## References

- Seed: seed-add-table-viewer-to-the-tui
- Related: seed-add-a-function-to-extract-flat-tables (in-memory extraction API)

## Blockers

- ms-24n1 [open] Load data in background worker using Polars/PyArrow for responsive viewing

## Linked

- ms-24n1 [open] Load data in background worker using Polars/PyArrow for responsive viewing

## Notes

**2026-02-08T18:51:06Z**

Documentation completed and committed.

**Summary:**
Created comprehensive documentation for the TUI table viewer in .

**Documentation covers:**
- Dual-source behavior (in-memory vs disk) with 🟢/🔵 indicators
- How to access the table viewer via View Tables button
- Row cap behavior (200 rows default) and performance rationale
- Supported table types (ttr_rankings, league_table, etc.)
- Polars/PyArrow usage for fast loading
- Lazy loading via  for disk-based tables
- Background workers for responsive UI
- Troubleshooting section

**Files changed:**
-  (new)
-  (updated with references)

**Commit:** 92f2584589bef09a4d7e1e1c75bdf7520991bdc2

All acceptance criteria met.
