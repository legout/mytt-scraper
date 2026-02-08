# Research: ms-nhyr - In-memory flat table extraction API

## Status
Research complete. Implementation ready to proceed.

## Context Reviewed

### Ticket Requirements
- Define public API: `extract_flat_tables(data, remaining=None, backend=...) -> dict[str, Any]`
- Support backends: polars, pandas, pyarrow
- Document return types for each backend
- Decide missing-table behavior (omit key vs empty table)
- Define deterministic column ordering (match CSV field lists)
- Maintain backward compatibility with existing CSV workflow

### Existing Codebase

#### Current Table Extraction (CSV-based)
Location: `src/mytt_scraper/utils/table_extractor.py`

Current functions write directly to CSV:
- `extract_club_info_table(block_data, tables_dir, prefix)`
- `extract_ttr_rankings_table(block_data, tables_dir, prefix)`
- `extract_league_table(block_data, tables_dir, prefix)`
- `extract_ttr_history_events_table(history, tables_dir, prefix)`
- `extract_ttr_history_matches_table(history, tables_dir, prefix)`

All use `write_csv()` helper that writes to disk.

#### Field Definitions (from config.py)
- `CLUB_INFO_FIELDS` - 6 fields
- `TTR_RANKING_FIELDS` - 20 fields  
- `LEAGUE_TABLE_FIELDS` - 10 fields
- `TTR_HISTORY_EVENTS_FIELDS` - 14 fields
- `TTR_HISTORY_MATCHES_FIELDS` - 38 fields

These define deterministic column ordering.

#### Dependencies
Already present in `pyproject.toml`:
- `polars>=1.38.1`
- `pandas>=3.0.0`
- `pyarrow>=23.0.0`

#### Data Structure
From `scraper.py`, the extraction works with:
- `data`: Main response data (parsed JSON)
- `remaining`: Deferred data text containing TTR history

The scraper currently extracts:
1. Club info from `data['pageContent']['blockLoaderData']`
2. TTR rankings from blocks with `'clubTtrRanking'`
3. League table from blocks with `'teamLeagueRanking'`
4. TTR history events/matches from parsed `remaining` text

## Design Decisions

### Backend Support Strategy
Use native return types for each backend:
- `backend="polars"` → `dict[str, polars.DataFrame]`
- `backend="pandas"` → `dict[str, pandas.DataFrame]`
- `backend="pyarrow"` → `dict[str, pyarrow.Table]`

### Missing-Table Behavior
**Decision**: Omit key from result dict (not empty table)

Rationale:
- Cleaner API - caller can use `if "table_name" in result`
- Consistent with Python dict conventions
- No ambiguity between "no data" and "data with zero rows"

### API Location
Create new module: `src/mytt_scraper/utils/in_memory_tables.py`

Export from package `__init__.py` for library consumers.

### Column Ordering
Match existing `*_FIELDS` lists from config.py exactly.

## Implementation Plan

1. Create `in_memory_tables.py` with:
   - `Backend` Literal type: `"polars" | "pandas" | "pyarrow"`
   - `extract_flat_tables(data, remaining, backend)` function
   - Internal extraction functions that return records (not write CSV)
   - Backend-specific conversion helpers

2. Update `utils/__init__.py` to export new function

3. Update main package `__init__.py` to export for library use

4. Add type stubs for clean IDE support

## Sources
- `src/mytt_scraper/utils/table_extractor.py` - existing extraction logic
- `src/mytt_scraper/config.py` - field definitions
- `src/mytt_scraper/scraper.py` - data structure and usage patterns
- `pyproject.toml` - dependency confirmation
- Seed: `seed-add-a-function-to-extract-flat-tables` - requirements
