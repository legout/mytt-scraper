---
id: ms-ay95
status: closed
deps: [ms-t6ic]
links: [ms-l9h9]
created: 2026-02-08T15:57:18Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-function-to-extract-flat-tables
tags: [tf, backlog, component:tests]
---
# Add fixture-based unit tests for extract_flat_tables()

## Task

Add unit tests that validate `extract_flat_tables(...)` using `tests/fixtures/community_response.json`.

## Context

We want confidence that the in-memory extraction returns the same tables/schemas as the CSV extraction path, and behaves well when sections are missing.

## Acceptance Criteria

- [ ] Tests cover at least one backend (pyarrow preferred) and validate column sets/order
- [ ] Tests verify that expected tables are present and non-empty where fixture provides data
- [ ] Tests cover missing-table behavior (as specified in API ticket)
- [ ] Tests run under the existing test harness (`.venv/bin/python ...` or pytest)

## References

- Seed: seed-add-a-function-to-extract-flat-tables
- Fixture: tests/fixtures/community_response.json


## Notes

**2026-02-08T16:19:00Z**

--message ## Implementation Complete

Added comprehensive fixture-based unit tests for extract_flat_tables():

**Test Coverage:**
- 21 unit tests across pyarrow (12), polars (2), and pandas (2) backends
- All 5 expected tables tested: club_info, ttr_rankings, league_table, ttr_history_events, ttr_history_matches
- Column set and order validation
- Non-empty table verification
- Missing table behavior (history tables omitted when no deferred data)
- Cross-backend consistency verification
- Backend validation (invalid backend raises ValueError)

**Acceptance Criteria:**
- ✅ Tests cover pyarrow backend (preferred)
- ✅ Validate column sets/order
- ✅ Verify expected tables present and non-empty
- ✅ Cover missing-table behavior
- ✅ Run under existing pytest harness

**Commit:** 78de5bb

**Artifacts:** .tf/knowledge/tickets/ms-ay95/
