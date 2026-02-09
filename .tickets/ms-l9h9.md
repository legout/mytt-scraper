---
id: ms-l9h9
status: closed
deps: [ms-t1zx]
links: [ms-t1zx, ms-t6ic, ms-ay95]
created: 2026-02-08T15:56:58Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-function-to-extract-flat-tables
tags: [tf, backlog, component:api, component:extractor]
---
# Implement extract_flat_tables() with pyarrow/pandas/polars backends

## Task

Implement `extract_flat_tables(data, remaining=None, backend=...)` that returns a dict of named tables converted to the requested backend: `pyarrow.Table`, `pandas.DataFrame`, or `polars.DataFrame`.

## Context

We already parse the fetched response into flat tables for CSV output. We want to reuse the same extraction logic but return in-memory tables for downstream analytics (DuckDB/Polars/Pandas) without intermediate files.

## Acceptance Criteria

- [ ] New function returns keys for available tables: club_info, ttr_rankings, league_table, ttr_history_events, ttr_history_matches
- [ ] Supports `backend in {"pyarrow", "pandas", "polars"}`
- [ ] Uses deterministic column ordering (existing field lists)
- [ ] Handles missing sections predictably (as specified in API ticket)
- [ ] Does not break existing CSV-writing code paths

## Constraints

- Avoid heavy conversions if backend is already PyArrow (prefer Arrow as canonical if practical)

## References

- Seed: seed-add-a-function-to-extract-flat-tables


## Notes

**2026-02-08T16:11:41Z**

--message ## Implementation Complete

extract_flat_tables() was already implemented with full support for pyarrow/pandas/polars backends.

### Verification Summary
- ✅ All 5 table types supported: club_info, ttr_rankings, league_table, ttr_history_events, ttr_history_matches
- ✅ All 3 backends working: pyarrow, pandas, polars
- ✅ Deterministic column ordering using config field lists
- ✅ Missing sections handled predictably (omitted from result)
- ✅ No impact on existing CSV code paths

### Code Location
- Implementation: src/mytt_scraper/utils/in_memory_tables.py
- Exported from: mytt_scraper (main package) and mytt_scraper.utils

### Review Results
- Critical: 0
- Major: 0
- Minor: 1 (acceptable type-ignore comments)
- Overall: COMPLIANT - Production ready

Commit: 7d7bdae
