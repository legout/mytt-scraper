# Research: ms-t1zx

## Status
Research completed via local codebase review. No external research needed.

## Context Reviewed
- Ticket: `ms-t1zx` - Refactor table_extractor to support in-memory extraction
- Current file: `src/mytt_scraper/utils/table_extractor.py`
- Seed: `seed-add-a-function-to-extract-flat-tables`

## Current Implementation Analysis

The `table_extractor.py` has 5 extraction functions that write CSV directly:

1. `extract_club_info_table()` - Extracts club metadata, writes to `club_info.csv`
2. `extract_ttr_rankings_table()` - Extracts TTR rankings, writes to `ttr_rankings.csv`
3. `extract_league_table()` - Extracts league standings, writes to `league_table.csv`
4. `extract_ttr_history_events_table()` - Extracts TTR history events
5. `extract_ttr_history_matches_table()` - Extracts matches from events (flattened)

All functions:
- Take `block_data` or `history` dict + `tables_dir` Path + optional `prefix`
- Use field lists from config: `CLUB_INFO_FIELDS`, `TTR_RANKING_FIELDS`, etc.
- Call `write_csv()` which handles the actual file I/O

## Refactoring Strategy

Per the seed and ticket requirements:
1. Create "getter" helpers that return `(rows, fieldnames)` tuples
2. Keep existing CSV-writing functions for backward compatibility
3. CSV functions will call the new getter helpers then write CSV

## Field Lists (from config)
- `CLUB_INFO_FIELDS` - Used by club_info extraction
- `TTR_RANKING_FIELDS` - Used by TTR rankings
- `LEAGUE_TABLE_FIELDS` - Used by league table
- `TTR_HISTORY_EVENTS_FIELDS` - Used by TTR history events
- `TTR_HISTORY_MATCHES_FIELDS` - Used by TTR history matches

## Sources
- Local codebase: `src/mytt_scraper/utils/table_extractor.py`
- Seed: `.tf/knowledge/topics/seed-add-a-function-to-extract-flat-tables/seed.md`
