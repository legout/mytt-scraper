---
id: ms-rhk9
status: open
deps: [ms-n639]
links: []
created: 2026-03-09T01:22:57Z
type: feature
priority: 0
assignee: legout
parent: ms-mvjw
tags: [feature, vertical-slice, web, search]
---
# Ship player search screen with SSE progress and result rendering

Implement full player search experience with mode toggle, async execution, and live results/progress/error updates.

## Design

PRD US-2/US-6; Spec 2.1(search),2.2(search signals),3.2; Plan P2.1-P2.5

## Acceptance Criteria

- [ ] /search presents query input and mode selector
- [ ] Search handler supports API and Playwright modes
- [ ] SSE updates drive searching/done/error and progress transitions
- [ ] Results render player identity, club, and TTR with selectable cards
- [ ] Error and empty-result states are visible and recoverable

