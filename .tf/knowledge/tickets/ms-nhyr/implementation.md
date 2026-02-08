# Implementation: ms-nhyr

## Summary
Defined the public API for in-memory flat table extraction from mytischtennis.de scraped data. The API supports multiple backends (Polars, Pandas, PyArrow) and returns structured tables without writing to CSV files.

## Files Changed

### 1. `src/mytt_scraper/utils/in_memory_tables.py` (NEW)
Main implementation file containing:
- `extract_flat_tables(data, remaining=None, *, backend="polars")` - Main entry point
- Backend support: `"polars"`, `"pandas"`, `"pyarrow"`
- Internal extraction functions that mirror CSV extraction logic
- Deterministic column ordering using config field lists
- Overloaded type hints for IDE support

Key design decisions:
- Missing tables are omitted from result (not returned as empty)
- Column order matches existing CSV field definitions
- Each backend returns native types (polars.DataFrame, pandas.DataFrame, pyarrow.Table)
- Full docstring with examples

### 2. `src/mytt_scraper/utils/__init__.py`
Added export for `extract_flat_tables` function.

### 3. `src/mytt_scraper/__init__.py`
Added export for `extract_flat_tables` at package level for library consumers.

## Key Decisions

### API Signature
```python
def extract_flat_tables(
    data: dict[str, Any],
    remaining: str | None = None,
    *,
    backend: Backend = "polars",
) -> dict[str, Any]
```

### Backend Return Types
- `"polars"` → `dict[str, polars.DataFrame]`
- `"pandas"` → `dict[str, pandas.DataFrame]`
- `"pyarrow"` → `dict[str, pyarrow.Table]`

### Missing-Table Behavior
Tables not present in data are omitted from the result dictionary (not returned as empty). This allows callers to check for presence with `if "table_name" in result`.

### Column Ordering
Deterministic ordering matches existing CSV field lists from config:
- `CLUB_INFO_FIELDS + ["extracted_at"]`
- `TTR_RANKING_FIELDS`
- `LEAGUE_TABLE_FIELDS`
- `TTR_HISTORY_EVENTS_FIELDS`
- `TTR_HISTORY_MATCHES_FIELDS`

## Tests Run

```python
# Verified import works
from mytt_scraper.utils.in_memory_tables import extract_flat_tables, Backend

# Tested all three backends with sample data
result = extract_flat_tables(sample_data, backend='polars')
# Tables extracted: ['club_info', 'ttr_rankings', 'league_table']
# All backends return correct types
```

## Verification

The API can be used as follows:

```python
from mytt_scraper import MyTischtennisScraper, extract_flat_tables

scraper = MyTischtennisScraper(username, password)
scraper.login()
data, remaining = scraper.fetch_own_community()
tables = extract_flat_tables(data, remaining, backend="polars")

# Access tables
tables["ttr_rankings"]  # polars.DataFrame
tables["club_info"]     # polars.DataFrame (single row)
```

## Backward Compatibility
Existing CSV workflow remains unchanged. The new API is purely additive.
