---
id: ms-fbpk
status: open
deps: [ms-rhk9, ms-a51k, ms-cz3f]
links: []
created: 2026-03-09T01:22:57Z
type: chore
priority: 2
assignee: legout
parent: ms-mvjw
tags: [chore, vertical-slice, web, testing, docs]
---
# Add web test suite, launch entrypoint, and usage documentation

Complete readiness work: web unit/integration tests, executable web entrypoint, and README updates.

## Design

PRD section 5/8; Spec section 6; Plan P4.3-P4.6

## Acceptance Criteria

- [ ] Signal tests validate defaults and key invariants
- [ ] Route integration tests cover auth guard and core route behaviors
- [ ] python -m mytt_scraper.web launches app and serves /health
- [ ] README documents web setup, launch, and feature scope
- [ ] Web tests run with project standard tooling (uv run pytest)

