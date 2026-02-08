# Research: ms-ay95

## Status
Research completed. Using existing project knowledge.

## Context Reviewed
- Ticket: Add fixture-based unit tests for extract_flat_tables()
- Seed topic: seed-add-a-function-to-extract-flat-tables
- Fixture: tests/fixtures/community_response.json (246KB)
- Source: src/mytt_scraper/utils/in_memory_tables.py
- Config: src/mytt_scraper/config.py (field definitions)

## Implementation Target

### Function to Test
`extract_flat_tables(data, remaining=None, *, backend="polars")` in `in_memory_tables.py`

### Expected Tables
- `club_info` - Single-row table with club information
- `ttr_rankings` - TTR rankings within the club
- `league_table` - League standings
- `ttr_history_events` - TTR history event summaries
- `ttr_history_matches` - Individual match details from TTR history

### Fixture Structure
The fixture `community_response.json` contains:
- `pageContent.blockLoaderData` with club info, TTR rankings, league table
- Top-level data keys with deferred TTR history data
- Format: `data:{json}\ndata:{error_json}` (multipart)

### Backends to Test
- `pyarrow` (preferred per ticket)
- `polars` (default, already used in project)
- `pandas` (for completeness)

### Test Scenarios
1. All backends return expected tables with correct columns
2. Tables are non-empty where fixture provides data
3. Missing tables (e.g., no remaining data) are omitted from result
4. Column order matches expected field definitions

## Sources
- Local fixture: tests/fixtures/community_response.json
- Source code: src/mytt_scraper/utils/in_memory_tables.py
