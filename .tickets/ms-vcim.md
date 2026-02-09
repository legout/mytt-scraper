---
id: ms-vcim
status: closed
deps: [ms-28lt]
links: [ms-fkf4, ms-28lt]
created: 2026-02-08T16:50:56Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-table-viewer-to-the-tui
tags: [tf, backlog, component:tui, component:viewer]
---
# Add "View Tables" entry + TableListScreen navigation in Textual TUI

## Task

Add a "View Tables" action to the Textual TUI and route it to a new `TableListScreen`.

## Context

Seed goal: users should preview extracted tables directly in the TUI after a fetch.
The viewer supports both in-memory tables (from current session) and disk-based CSV files.
Spike recommends Textual's `DataTable` for rendering and a simple list screen for choosing a table.

## Acceptance Criteria

- [ ] Main menu includes "View Tables" (disabled/hidden if no tables available)
- [ ] Selecting it opens a placeholder `TableListScreen`
- [ ] Navigation back to the main menu works
- [ ] The viewer checks for in-memory tables first (from recent fetch), then disk CSVs
- [ ] Store in-memory tables in app state for session-wide access

## Constraints

- Keep MVP simple (no fancy layout)
- Must integrate with existing fetch workflows that may use `extract_flat_tables()`

## References

- Seed: seed-add-table-viewer-to-the-tui
- Spike: spike-table-viewer-for-python-tui-textual (DataTable + simple selection screen)
- Related: seed-add-a-function-to-extract-flat-tables (in-memory Polars extraction)

## Blockers

- ms-28lt [open] Add MainMenuScreen + actions: fetch own profile / fetch by user-id

## Blocking

- ms-fkf4 [open] Implement table discovery (in-memory + disk) with friendly names

## Linked

- ms-fkf4 [open] Implement table discovery (in-memory + disk) with friendly names
- ms-28lt [open] Add MainMenuScreen + actions: fetch own profile / fetch by user-id

## Notes

**2026-02-08T18:37:18Z**

Implementation complete.

Changes:
- Added 'View Tables' button to MainMenuScreen (disabled when no tables available)
- Created TableListScreen for selecting and viewing tables
- Added reactive 'tables' state to MyttScraperApp for session-wide in-memory table storage
- Modified fetch operations to extract and store tables using extract_flat_tables()
- Navigation: MainMenu → TableList → TablePreview → back navigation works

Commit: feafd33
All existing tests pass.
