---
id: ms-lxid
status: closed
deps: [ms-dxg2]
links: [ms-dxg2, ms-861m]
created: 2026-02-08T19:24:57Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-comprehensive-documentation-using-th
tags: [tf, backlog, docs, component:docs, component:cli, component:tui]
---
# Author how-to: Search players and fetch external profile (CLI + TUI)

## Task

Write how-to guides for searching and fetching external profiles, covering both CLI and TUI where applicable.

## Context

Users often want to find opponents and fetch their data quickly.

## Acceptance Criteria

- [ ] Create `docs/how-to/search-players.md`
- [ ] Create `docs/how-to/fetch-external-profile.md`
- [ ] Each includes CLI steps + (if available) TUI screen flow
- [ ] Notes API vs Playwright search options

## References

- Plan: plan-diataxis-documentation-cli-repl-tui


## Notes

**2026-02-08T23:21:55Z**

## Implementation Complete

Created two how-to guides covering CLI and TUI workflows:

**docs/how-to/search-players.md**
- Mode 4 (interactive) and Mode 5 (batch) CLI workflows
- TUI screen-by-screen walkthrough (Search → Select → Batch Fetch)
- API vs Playwright comparison table and usage guidance
- Search tips and troubleshooting

**docs/how-to/fetch-external-profile.md**
- 3 methods for finding user IDs
- CLI workflow with custom prefix options
- TUI workflow with modal dialog and progress tracking
- Complete output file reference (all 5 CSV types)
- File organization tips

**Updated:** docs/how-to/index.md (renamed link to match new filename)

**Commit:** e012ac7
