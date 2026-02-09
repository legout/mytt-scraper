---
id: ms-t1zx
status: closed
deps: [ms-nhyr]
links: [ms-l9h9]
created: 2026-02-08T15:56:45Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-a-function-to-extract-flat-tables
tags: [tf, backlog, component:extractor]
---
# Refactor table_extractor to support in-memory extraction

## Task

Refactor `src/mytt_scraper/utils/table_extractor.py` so table extraction can produce in-memory rows (and fieldnames) without writing CSV, while preserving the existing CSV output behavior.

## Context

Current extraction functions write CSV directly. The new in-memory API will need reusable extraction primitives that return data structures (e.g., list[dict]) that can then be converted to Arrow/Pandas/Polars.

## Acceptance Criteria

- [ ] Add helpers that return rows for each table (club_info, ttr_rankings, league_table, ttr_history_events, ttr_history_matches)
- [ ] Existing CSV-writing path still works and continues to write identical columns
- [ ] Column ordering remains deterministic (matches existing field lists)
- [ ] No extra filesystem writes are required for in-memory callers

## Constraints

- Keep changes localized (prefer additive helpers + small refactor)

## References

- Seed: seed-add-a-function-to-extract-flat-tables


## Notes

**2026-02-08T16:09:17Z**

--message Implementation complete.

Refactored table_extractor.py to support in-memory extraction:
- Added 5 new getter helpers (get_club_info_rows, get_ttr_rankings_rows, get_league_table_rows, get_ttr_history_events_rows, get_ttr_history_matches_rows)
- All existing CSV functions now call the new helpers internally
- Full backward compatibility maintained
- No filesystem I/O required for in-memory callers

Commit: e3aebf4
