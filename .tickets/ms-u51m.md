---
id: ms-u51m
status: closed
deps: []
links: []
created: 2026-03-09T01:22:57Z
type: feature
priority: 1
assignee: legout
parent: ms-mvjw
tags: [feature, vertical-slice, web, foundation]
---
# Scaffold web package, app factory, and health boot path

Create initial web surface end-to-end: dependencies, package scaffold, app factory wiring, base layout, and /health endpoint.

## Design

PRD 4.1/4.2/4.5; Spec 1.3,2.1,5.3; Plan P0.1-P0.5

## Acceptance Criteria

- [ ] pyproject includes web extras for StarHTML/StarUI and runtime deps
- [ ] src/mytt_scraper/web module tree exists and imports cleanly
- [ ] create_app() builds app and registers route modules
- [ ] /health returns HTTP 200 with healthy payload
- [ ] Shared layout shell renders title/branding


## Notes

**2026-03-09T01:53:40Z**

Implementation complete:

- Added web extras to pyproject.toml (starhtml>=0.5.0, starui>=0.1.0)
- Created web package with create_app() factory and route registration
- Implemented /health endpoint returning {status: 'healthy', timestamp: ...}
- Added PageLayout component with title/branding (starhtml primitives)
- All acceptance criteria verified: imports work, health endpoint functional

Commit: e70abc4
Files: 12 new files in src/mytt_scraper/web/
