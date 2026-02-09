---
id: ms-btdf
status: closed
deps: [ms-xj1i]
links: [ms-xj1i, ms-44ps]
created: 2026-02-08T19:24:57Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-comprehensive-documentation-using-th
tags: [tf, backlog, docs, component:docs, component:build]
---
# Add Zensical configuration + Diátaxis nav skeleton

## Task

Add `zensical.toml` (or compatible config) and a minimal nav that reflects the Diátaxis structure.

## Context

Spike shows typical Zensical usage: `zensical new .`, `zensical serve`, `zensical build`. We can add config manually and integrate gradually.

## Acceptance Criteria

- [ ] Add `zensical.toml` at repo root
- [ ] Nav includes Tutorials / How-To / Reference / Explanation sections
- [ ] Local commands documented: `uv run zensical serve` and `uv run zensical build`

## References

- Plan: plan-diataxis-documentation-cli-repl-tui
- Spike: spike-documentation-of-python-projects-using-z


## Notes

**2026-02-08T23:31:51Z**

## Implementation Complete

Added Zensical configuration and Diátaxis navigation skeleton:

**Changes:**
- Created  with Diátaxis nav structure (Tutorials/How-To/Reference/Explanation)
- Added  to dev dependencies in 
- Updated README.md with local Zensical commands documentation
- Created  with contributor guide

**Local Commands:**
-  - preview docs with hot reload
-  - build static site

**Commit:** 816fb15
