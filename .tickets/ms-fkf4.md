---
id: ms-fkf4
status: closed
deps: [ms-vcim]
links: [ms-vcim, ms-b7cc]
created: 2026-02-08T16:50:56Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-table-viewer-to-the-tui
tags: [tf, backlog, component:viewer, component:io]
---
# Implement table discovery (in-memory + disk) with friendly names

## Task

Implement discovery of available tables from both in-memory sources (current session) and disk (`tables/`), mapping them to friendly table names shown in the TUI.

## Context

The TUI should show a list of tables a user can preview (e.g., `ttr_rankings`, `league_table`, etc.). Tables can come from:
1. **In-memory**: Polars DataFrames / PyArrow Tables from the current session (if `extract_flat_tables` was used)
2. **Disk**: CSV files in `tables/` (fallback)

## Acceptance Criteria

- [ ] Create a `TableProvider` abstraction that hides in-memory vs disk source differences
- [ ] Check for in-memory tables first (stored in app state from recent fetches)
- [ ] Scan `tables/` for `*.csv` as fallback for tables not in memory
- [ ] Detect known table types by filename suffix or in-memory table name (e.g. `*_ttr_rankings.csv`)
- [ ] Provide a stable display label (table type + optional prefix)
- [ ] Indicate source in UI (memory vs disk) with icons or labels
- [ ] Handles empty sources gracefully (no crash)

## Constraints

- Must not load full table data during discovery (metadata only)

## References

- Seed: seed-add-table-viewer-to-the-tui
- Related: seed-add-a-function-to-extract-flat-tables (in-memory extraction)
- Docs: docs/USAGE.md

## Blockers

- ms-vcim [open] Add "View Tables" entry + TableListScreen navigation in Textual TUI

## Blocking

- ms-b7cc [open] Build TablePreviewScreen using Textual DataTable

## Linked

- ms-vcim [open] Add "View Tables" entry + TableListScreen navigation in Textual TUI
- ms-b7cc [open] Build TablePreviewScreen using Textual DataTable

## Notes

**2026-02-08T18:41:57Z**

Implemented TableProvider abstraction for unified table discovery.

Changes:
- Created TableProvider with InMemoryTableProvider and DiskTableProvider
- TableListScreen now shows tables from both sources with source indicators (🟢/🔵)
- Friendly display names with prefix support (e.g., 'abc123 - TTR Rankings')
- Memory tables take precedence over disk tables
- Fast metadata-only discovery (no full data loading)

Commit: 85bea3da9ed6c95ad6f9482d06e06ba6b6f1d529
