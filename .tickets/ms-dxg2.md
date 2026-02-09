---
id: ms-dxg2
status: closed
deps: [ms-qm00]
links: [ms-qm00, ms-lxid]
created: 2026-02-08T19:24:56Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-comprehensive-documentation-using-th
tags: [tf, backlog, docs, component:docs, component:cli]
---
# Author tutorial: First run (install + Playwright + login + fetch own profile)

## Task

Write the first tutorial guiding a new user from install to first successful fetch.

## Context

This is the highest value onboarding content. Keep it copy/paste ready and safe (no credential leaks).

## Acceptance Criteria

- [ ] Create `docs/tutorials/first-run.md`
- [ ] Covers: `uv sync`, Playwright install, running CLI, choosing mode 1
- [ ] Mentions where outputs are written (`tables/`)
- [ ] Includes troubleshooting for headed mode and captcha

## References

- Plan: plan-diataxis-documentation-cli-repl-tui


## Notes

**2026-02-08T23:18:54Z**

Implemented first-run tutorial (docs/tutorials/first-run.md)

Created comprehensive tutorial covering:
- uv sync installation
- Playwright browser setup
- CLI usage with mode 1 (own profile)
- Output location (tables/ directory)
- Troubleshooting for headed mode and captcha issues

Commit: d6076ab

All acceptance criteria met. Tutorial is copy/paste ready and security-conscious (no credential storage).
