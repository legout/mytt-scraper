---
id: ms-6kxp
status: closed
deps: [ms-28lt]
links: [ms-28lt, ms-j0ge]
created: 2026-02-08T16:43:43Z
type: task
priority: 2
assignee: legout
external-ref: plan-choose-textual-for-creating-the-tui
tags: [tf, backlog, plan, component:tui, component:search]
---
# Implement SearchScreen (API search + Playwright fallback) and show results list

## Task

Implement a Search screen that runs player search (API first, optional Playwright fallback) and displays results in a selectable list.

## Context

The repo already has `PlayerSearcher.search_players(...)`. The TUI needs a UI to enter a query, run the search, and display results.

## Acceptance Criteria

- [ ] User can enter a query and trigger search
- [ ] Search uses API by default and can switch to Playwright mode
- [ ] Results are shown in a list with key fields (name, club, ttr, user-id)
- [ ] Selecting a row exposes the user-id for subsequent fetch

## References

- Plan: plan-choose-textual-for-creating-the-tui


## Notes

**2026-02-08T17:28:21Z**

Implemented SearchScreen with full functionality:

**Changes:**
- Added search mode toggle (API/Playwright) using Switch widget
- Implemented results DataTable with columns: Name, Club, TTR, User ID
- Added row selection that exposes user-id for fetch
- Background worker for non-blocking search operations
- Keyboard shortcuts: Enter (select/fetch), f (fetch), Escape (back)
- Added CSS styles for search options, results table, and selection bar

**Files Modified:**
- src/mytt_scraper/tui/screens.py
- src/mytt_scraper/tui/app.py

**Commit:** 0a69476

**Review:** 0 issues found (Critical:0, Major:0, Minor:0, Warnings:0, Suggestions:0)

**Acceptance Criteria:**
✓ User can enter query and trigger search
✓ Search uses API by default, can switch to Playwright
✓ Results shown with name, club, ttr, user-id
✓ Selecting row exposes user-id for fetch
