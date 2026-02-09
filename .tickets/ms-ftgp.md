---
id: ms-ftgp
status: closed
deps: [ms-0824]
links: [ms-0824, ms-b2hw]
created: 2026-02-08T17:14:58Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-filters-and-advanced-queries-to-the
tags: [tf, backlog, component:tui, component:viewer, component:query]
---
# Add Textual UI: filter panel + apply/reset actions

## Task

Add a simple filter UI to the table viewer screen(s): choose column, operator, value; then apply/reset and refresh preview.

## Context

MVP UI should support common operations without a full query editor.

## Acceptance Criteria

- [ ] UI controls for column + operator + value
- [ ] Apply action runs query in a background worker and refreshes DataTable
- [ ] Reset action clears query and shows base preview
- [ ] Validation errors are shown (invalid column/value/type)

## References

- Seed: seed-add-filters-and-advanced-queries-to-the
- Table viewer: seed-add-table-viewer-to-the-tui


## Notes

**2026-02-08T18:04:59Z**

Implemented TablePreviewScreen with filter panel UI.

Changes:
- Added TablePreviewScreen with column/operator/value filter controls
- Apply action runs query in background worker using PolarsQueryExecutor
- Reset action clears filter and restores base preview
- Validation errors displayed for invalid column/value/type
- Supports both in-memory Polars DataFrames and CSV files
- Keyboard shortcuts: 'a' apply, 'r' reset, 'escape' back

Files modified:
- src/mytt_scraper/tui/screens.py
- src/mytt_scraper/tui/app.py

Commit: b049636

Review: 0 critical, 0 major, 2 minor issues (cosmetic)
All acceptance criteria met.
