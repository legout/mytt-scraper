# Implementation: ms-fkf4

## Summary

Implemented table discovery (in-memory + disk) with friendly names for the TUI. Created a `TableProvider` abstraction that unifies access to both in-memory tables (from current session) and disk-based tables (CSV files in `tables/`).

## Files Changed

1. **`src/mytt_scraper/utils/table_provider.py`** (new file)
   - `TableSource` enum - distinguishes MEMORY vs DISK sources
   - `TableInfo` dataclass - metadata for discovered tables (name, display_name, table_type, source, row_count, etc.)
   - `InMemoryTableProvider` - discovers and accesses in-memory Polars/PyArrow tables
   - `DiskTableProvider` - discovers CSV files with metadata-only access (fast line counting)
   - `TableProvider` - unified provider combining both sources (memory takes precedence)
   - `create_default_provider()` - factory function for easy setup

2. **`src/mytt_scraper/utils/__init__.py`**
   - Added exports for all table provider classes

3. **`src/mytt_scraper/tui/app.py`**
   - Added `get_table_provider()` method - returns configured TableProvider
   - Added `discover_tables()` method - returns list of TableInfo from all sources
   - Added `has_any_tables()` method - checks memory and disk for available tables

4. **`src/mytt_scraper/tui/screens.py`**
   - Updated `TableListScreen` to use TableProvider for discovery
   - Added source indicator icons (🟢 in-memory, 🔵 disk)
   - Added source legend to the UI
   - Updated `_open_table()` to handle both memory and disk sources
   - Updated `MainMenuScreen._update_view_tables_button()` to check disk tables too

## Key Decisions

### Table Type Detection
- Detects known table types by filename suffix/prefix pattern: `{prefix}_{table_type}`
- Known types: `ttr_rankings`, `league_table`, `club_info`, `ttr_history_events`, `ttr_history_matches`, `tournament_registrations`
- Unknown types fallback to filename with title-case formatting

### Source Precedence
- In-memory tables take precedence over disk tables with the same name
- Disk tables are only shown if not shadowed by in-memory version

### Display Names
- Known types get friendly names: "TTR Rankings", "League Table", etc.
- Prefixed tables show prefix: "abc123 - TTR Rankings"
- Unknown types use title-cased filename: "unknown_custom_table" → "Unknown Custom Table"

### Metadata-Only Discovery
- Disk provider uses fast line counting (not full CSV parsing)
- Returns row count without loading data
- Data only loaded when table is actually opened

### Empty Source Handling
- Gracefully handles missing `tables/` directory
- Returns empty list when no tables found
- No crashes on any error conditions

## Tests Run

Created and ran test script covering:
- In-memory provider with known/unknown table types
- Disk provider with CSV file discovery
- Combined provider with source precedence
- Empty source handling
- Row counting for both sources

All tests passed.

## Verification

To verify the implementation:

1. Run TUI and login: `python -m mytt_scraper.tui`
2. Fetch profile data (creates in-memory tables)
3. Click "View Tables" button (now enabled when disk tables exist too)
4. See list with:
   - 🟢 Green icon for in-memory tables
   - 🔵 Blue icon for disk tables
   - Friendly display names
   - Row counts
   - Source indicators
5. Select a table to open preview screen
6. Both memory and disk tables open correctly

## Acceptance Criteria Status

- [x] Create a `TableProvider` abstraction that hides in-memory vs disk source differences
- [x] Check for in-memory tables first (stored in app state from recent fetches)
- [x] Scan `tables/` for `*.csv` as fallback for tables not in memory
- [x] Detect known table types by filename suffix or in-memory table name
- [x] Provide a stable display label (table type + optional prefix)
- [x] Indicate source in UI (memory vs disk) with icons or labels
- [x] Handles empty sources gracefully (no crash)
- [x] Does not load full table data during discovery (metadata only)
