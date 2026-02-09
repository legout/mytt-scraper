---
id: ms-44ps
status: closed
deps: [ms-btdf]
links: [ms-btdf, ms-xy4t]
created: 2026-02-08T19:24:57Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-comprehensive-documentation-using-th
tags: [tf, backlog, docs, component:ci, component:docs]
---
# Add CI job to build docs with Zensical

## Task

Add a CI workflow step that installs deps and runs `uv run zensical build` to ensure docs don't break.

## Acceptance Criteria

- [ ] CI runs `uv sync` (include docs deps if separated)
- [ ] CI runs `uv run zensical build`
- [ ] Build failures fail the pipeline

## References

- Plan: plan-diataxis-documentation-cli-repl-tui
- Spike: spike-documentation-of-python-projects-using-z


## Notes

**2026-02-08T23:33:52Z**

Implemented CI workflow for documentation builds.

Changes:
- Added .github/workflows/docs.yml with uv setup and zensical build
- Fixed zensical.toml to use correct site_name format

Commit: d054c6e
Build tested locally and passes.
