---
id: ms-xy4t
status: closed
deps: [ms-44ps]
links: [ms-44ps]
created: 2026-02-08T19:24:57Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-comprehensive-documentation-using-th
tags: [tf, backlog, docs, component:docs]
---
# Add "Contributing to docs" page (preview/build/style rules)

## Task

Add a contributor-focused documentation page describing how to preview/build docs locally and basic style rules.

## Acceptance Criteria

- [ ] Create `docs/how-to/contribute-docs.md` (or `docs/reference/contributing-docs.md`)
- [ ] Includes: install, preview (`zensical serve`), build (`zensical build`)
- [ ] Includes naming conventions and where to add new pages

## References

- Plan: plan-diataxis-documentation-cli-repl-tui


## Notes

**2026-02-08T23:35:35Z**

Implemented: Added 'Contributing to docs' how-to guide

Changes:
- Created docs/how-to/contribute-docs.md with local preview/build instructions
- Updated zensical.toml navigation
- Updated docs/how-to/index.md with link to new guide

Commit: e5855ee
Build: Verified with 'uv run zensical build' - passes
