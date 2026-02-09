---
id: ms-nhyr
status: closed
deps: []
links: []
created: 2026-02-08T15:56:33Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-function-to-extract-flat-tables
tags: [tf, backlog, component:api]
---
# Define in-memory flat table extraction API

## Task

Define the public API for extracting the scraper's flat tables in-memory (no CSV writes), including backend selection and missing-table behavior.

## Context

The scraper currently extracts tables by writing CSV files. Library consumers want the same tables as Polars/Pandas/PyArrow objects directly from fetched `data` (+ optional deferred `remaining`).

## Acceptance Criteria

- [ ] A single entry point is specified: `extract_flat_tables(data, remaining=None, backend=...) -> dict[str, Any]`
- [ ] Backend values and return types are documented (`polars`, `pandas`, `pyarrow`)
- [ ] Missing-table behavior is decided (omit key vs empty table) and documented
- [ ] Deterministic column ordering is defined (match existing CSV field lists)

## Constraints

- Backward compatible: existing CSV workflow remains unchanged

## References

- Seed: seed-add-a-function-to-extract-flat-tables


## Notes

**2026-02-08T16:05:57Z**

--note ## Implementation Complete ✅

**API Defined**: 

**Files Added**:
-  - Main implementation
- Updated exports in  files

**Backend Support**:
-  → returns 
-  → returns 
-  → returns 

**Design Decisions**:
- Missing tables are omitted from result (not returned as empty)
- Deterministic column ordering matches existing CSV field lists from config
- Full type hints with @overload for IDE support

**Quality**: 0 critical, 0 major issues. 4 minor fixes applied.

**Commit**: dab81a3
