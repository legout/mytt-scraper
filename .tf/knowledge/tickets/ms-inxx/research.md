# Research: ms-inxx

## Status
Research enabled. Ticket is straightforward - documentation task for existing feature.

## Context Reviewed
- `tk show ms-inxx` - Document in-memory flat table extraction usage
- Seed: `seed-add-a-function-to-extract-flat-tables` - Original feature specification
- Linked ticket: ms-t6ic (closed) - Expose scraper-level helper

## Existing Implementation

### API Location
- `src/mytt_scraper/utils/in_memory_tables.py` - Core `extract_flat_tables()` function
- `src/mytt_scraper/scraper.py` - `MyTischtennisScraper.extract_flat_tables()` convenience wrapper

### Function Signature
```python
def extract_flat_tables(
    data: dict[str, Any],
    remaining: str | None = None,
    *,
    backend: Backend = "polars",  # "polars", "pandas", or "pyarrow"
) -> dict[str, Any]
```

### Supported Backends
- `"polars"` - Returns Polars DataFrames (default)
- `"pandas"` - Returns Pandas DataFrames
- `"pyarrow"` - Returns PyArrow Tables

### Return Value
Dictionary with table names as keys:
- `club_info` - Single-row table with club information
- `ttr_rankings` - TTR rankings within the club
- `league_table` - League standings
- `ttr_history_events` - TTR history event summaries
- `ttr_history_matches` - Individual match details

**Missing tables are omitted** (not returned as empty).

### Usage Patterns
```python
# Method 1: Via scraper instance method
scraper = MyTischtennisScraper(username, password)
scraper.login()
data, remaining = scraper.fetch_own_community()
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Method 2: Via standalone function
from mytt_scraper.utils.in_memory_tables import extract_flat_tables
tables = extract_flat_tables(data, remaining, backend="pandas")
```

## Tests
- `tests/test_in_memory_tables.py` - Comprehensive test coverage for all 3 backends
- Tests verify: table presence, columns, row counts, missing data behavior

## Documentation Requirements (from ticket)
- README (or docs) includes minimal snippet: login → fetch → extract_flat_tables
- Documents backend selection and missing-table behavior
- Mentions that CSV extraction remains available and unchanged

## Sources
- `src/mytt_scraper/utils/in_memory_tables.py`
- `src/mytt_scraper/scraper.py`
- `tests/test_in_memory_tables.py`
- `README.md` (current)
