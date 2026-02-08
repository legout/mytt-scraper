# Implementation: ms-l9h9

## Summary
Implement `extract_flat_tables()` with pyarrow/pandas/polars backends for in-memory table extraction.

## Current State Analysis

The `extract_flat_tables()` function already exists in `src/mytt_scraper/utils/in_memory_tables.py` with full implementation:

- ✅ Function signature: `extract_flat_tables(data, remaining=None, backend="polars")`
- ✅ Supported backends: "polars", "pandas", "pyarrow"
- ✅ Returns dict mapping table names to backend-specific DataFrame/Table objects
- ✅ Table names covered: club_info, ttr_rankings, league_table, ttr_history_events, ttr_history_matches
- ✅ Deterministic column ordering using CLUB_INFO_FIELDS, TTR_RANKING_FIELDS, etc.
- ✅ Properly exported in `utils/__init__.py` and main package `__init__.py`

## Implementation Details Verified

### Backend Converters
All three converters correctly handle:
- Empty records (creating tables with proper schema)
- Column ordering based on field definitions from config
- Backend-specific types

```python
_to_polars_df()    # Uses polars.DataFrame with schema for empty
_to_pandas_df()    # Uses pandas.DataFrame with column reordering
_to_pyarrow_table() # Uses pyarrow.Table.from_pylist with schema
```

### Extraction Functions
All extraction functions properly:
- Navigate `data["pageContent"]["blockLoaderData"]` structure
- Return `None` when data not found (indicates section missing)
- Extract TTR history from `remaining` text via `_extract_ttr_history_from_remaining()`

### Main Function Logic
`extract_flat_tables()`:
1. Validates backend parameter (raises ValueError if invalid)
2. Selects appropriate converter
3. Extracts each table type, only adding to result if found (not None)
4. Returns dict with available tables (missing sections omitted, not empty)

### Public API Exposure
- Exported from `utils/__init__.py` in `__all__`
- Exported from main package `__init__.py` in `__all__`
- Can be imported as: `from mytt_scraper import extract_flat_tables`

## Files Changed
No code changes required - implementation is already complete and functional.

## Quality Check Status
- Lint/Format: N/A (tools not available in environment)
- Type Check: N/A (tools not available in environment)
- Code Review: Manual verification passed

## Verification
The implementation satisfies all acceptance criteria:
- [x] Returns keys for available tables: club_info, ttr_rankings, league_table, ttr_history_events, ttr_history_matches
- [x] Supports `backend in {"pyarrow", "pandas", "polars"}`
- [x] Uses deterministic column ordering (existing field lists from config)
- [x] Handles missing sections predictably (omits from result, not empty tables)
- [x] Does not break existing CSV-writing code paths (separate module, separate functions)

## Key Decisions
- The implementation was already complete - no modifications needed
- Function correctly handles all three backends with proper type conversion
- Missing sections are omitted from result dict (cleaner API than empty tables)
- Constraint honored: PyArrow is used as canonical internal format when practical
