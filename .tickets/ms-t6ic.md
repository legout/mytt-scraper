---
id: ms-t6ic
status: closed
deps: [ms-l9h9]
links: [ms-l9h9, ms-inxx]
created: 2026-02-08T15:57:08Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-function-to-extract-flat-tables
tags: [tf, backlog, component:core]
---
# Expose scraper-level helper to extract flat tables from fetched data

## Task

Expose a convenient library-facing helper (method or wrapper) on `MyTischtennisScraper` to produce in-memory flat tables from fetched profile data.

## Context

Callers will typically do:
1) login
2) fetch profile (`fetch_own_community` / `fetch_external_profile`)
3) extract tables

They should be able to call a method like `scraper.extract_flat_tables(data, remaining, backend=...)` (or similar) without knowing internal module paths.

## Acceptance Criteria

- [ ] Public helper is available from the main package (document import path)
- [ ] Helper delegates to `extract_flat_tables(...)`
- [ ] Works with both own profile and external profile fetched data
- [ ] Does not change existing CLI behavior

## References

- Seed: seed-add-a-function-to-extract-flat-tables


## Notes

**2026-02-08T16:14:49Z**

Implemented scraper.extract_flat_tables() method

Changes:
- Added extract_flat_tables() method to MyTischtennisScraper class
- Method delegates to the existing module-level extract_flat_tables() function
- Supports polars/pandas/pyarrow backends
- Works with both own profile and external profile data
- Added Backend type alias for better type safety

Public API:
- from mytt_scraper import extract_flat_tables (module-level)
- scraper.extract_flat_tables(data, remaining, backend=...) (instance method)

Commit: b7eb5a8
