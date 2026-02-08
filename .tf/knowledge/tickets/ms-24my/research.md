# Research: ms-24my - Document TUI table viewer usage + data sources

## Ticket Summary
Document how to use the table viewer in the Textual TUI, including the dual-source approach (in-memory vs disk), row limits, and performance considerations.

## Context Reviewed

### Existing Documentation
- `/docs/TUI_TABLE_QUERIES.md` - Comprehensive guide on filters, sorting & queries
- `/docs/USAGE.md` - Table schemas and data formats
- `/README.md` - General TUI usage

### Codebase References
- `src/mytt_scraper/tui/screens.py` - Contains `TableListScreen` and `TablePreviewScreen`
- `src/mytt_scraper/utils/table_provider.py` - Dual-source provider implementation
- `src/mytt_scraper/tui/app.py` - Table provider integration

### Topic Knowledge
- `seed-add-table-viewer-to-the-tui/` - Original seed for table viewer feature
- `seed-add-a-function-to-extract-flat-tables/` - Related in-memory extraction API

## Key Findings

### Dual-Source Behavior
The TUI table viewer uses a `TableProvider` class that combines two sources:

1. **In-Memory Tables (Primary)**
   - Source: `TableSource.MEMORY`
   - Stored as Polars DataFrames or PyArrow Tables
   - From current session's fetched data via `extract_flat_tables()`
   - Indicator: 🟢 (green circle)
   - Displayed with primary button variant

2. **Disk-Based Tables (Fallback)**
   - Source: `TableSource.DISK`
   - CSV files in `tables/` directory
   - Indicator: 🔵 (blue circle)
   - Loaded lazily using Polars `pl.scan_csv()` + `.head(limit).collect()`
   - Row count via fast line counting (not full parsing)

### Row Cap Behavior
- Default limit: **200 rows** (see `TablePreviewScreen.__init__`)
- Purpose: Performance (UI responsiveness, memory usage)
- Applied to both memory and disk sources
- For disk: Uses lazy evaluation (`scan_csv().head().collect()`)
- Status shows: "Showing {displayed} of {total} rows"

### Supported Table Types
From `KNOWN_TABLE_TYPES` in `table_provider.py`:
- `ttr_rankings` → "TTR Rankings"
- `league_table` → "League Table"
- `club_info` → "Club Info"
- `ttr_history_events` → "TTR History Events"
- `ttr_history_matches` → "TTR History Matches"
- `tournament_registrations` → "Tournament Registrations"

### Performance Implementation
- **Polars/PyArrow**: Used for fast loading and operations
- **Lazy loading**: Disk tables use `pl.scan_csv()` with `.head(limit).collect()`
- **Background workers**: Data loading runs in `Worker` threads
- **Row counting**: Fast line-count for disk files without parsing

### Navigation
- Access via "View Tables" button in Main Menu (enabled when tables exist)
- `TableListScreen` shows available tables with source indicators
- Selecting opens `TablePreviewScreen` with query/filter capabilities

## Documentation Gap
The existing `TUI_TABLE_QUERIES.md` focuses on filters/sorting but doesn't cover:
1. How to open/access the table viewer
2. The dual-source concept (memory vs disk)
3. Row cap behavior and why it exists
4. The source indicator icons
5. How tables become available (fetch → extract → in-memory → disk)

## Research Decision
No external research needed - all information is available in the codebase and existing topic knowledge.
