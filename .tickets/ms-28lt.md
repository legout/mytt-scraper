---
id: ms-28lt
status: closed
deps: [ms-rprw]
links: [ms-rprw, ms-6kxp, ms-vcim]
created: 2026-02-08T16:43:43Z
type: task
priority: 2
assignee: legout
external-ref: plan-choose-textual-for-creating-the-tui
tags: [tf, backlog, plan, component:tui, component:core]
---
# Add MainMenuScreen + actions: fetch own profile / fetch by user-id

## Task

Add a main menu screen with actions to fetch own profile data and fetch an external profile by user-id, showing progress and an output summary.

## Context

These are the core workflows already supported by the scraper; the TUI should orchestrate them and show where CSVs were written.

## Acceptance Criteria

- [ ] Main menu lists actions and routes to the right handler
- [ ] Fetch own profile runs and reports success/failure
- [ ] Fetch external profile prompts for user-id and runs
- [ ] After each action, show a short summary (e.g., tables written to `tables/`)

## References

- Plan: plan-choose-textual-for-creating-the-tui


## Notes

**2026-02-08T17:25:25Z**

-- ## Implementation Complete

**Commit:** 6563bfc

**Summary:**
Implemented MainMenuScreen with full functionality for fetching own profile and fetching external profiles by user ID.

**Changes:**
- src/mytt_scraper/tui/screens.py - Rewrote MainMenuScreen with background workers; added UserIdInputScreen and ResultScreen modals
- src/mytt_scraper/tui/app.py - Registered new screens, added CSS styles

**Features:**
1. Fetch My Profile - runs in background worker, shows result summary
2. Fetch by User ID - prompts for user ID in modal, then fetches profile
3. After each action, shows ResultScreen with tables written summary

**Acceptance Criteria:**
- [x] Main menu lists actions and routes to handlers
- [x] Fetch own profile runs and reports success/failure
- [x] Fetch external profile prompts for user-id and runs
- [x] After each action, shows short summary (tables directory + files)
