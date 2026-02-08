# Fixes: ms-nhyr

## Summary
Applied 4 minor fixes identified during review. No critical or major issues were found.

## Fixes Applied

### 1. Removed Unused TypeVar Import
**Location**: `src/mytt_scraper/utils/in_memory_tables.py:22`
**Issue**: `TypeVar("T")` was imported but never used.
**Fix**: Removed the import and the unused `T = TypeVar("T")` assignment.

### 2. Added Comments for Type Ignore Annotations
**Location**: `src/mytt_scraper/utils/in_memory_tables.py`
**Files changed**:
- `_to_polars_df` - Added comment: `# type: ignore[return]  # Conditional import, return type is polars.DataFrame`
- `_to_pandas_df` - Added comment: `# type: ignore[return]  # Conditional import, return type is pandas.DataFrame`
- `_to_pyarrow_table` - Added comment: `# type: ignore[return]  # Conditional import, return type is pyarrow.Table`

**Rationale**: Explains why type checking is suppressed (conditional imports inside functions).

### 3. Improved Club Info Detection Heuristic
**Location**: `src/mytt_scraper/utils/in_memory_tables.py:51-56`
**Issue**: Previous heuristic used `any()` which could match blocks that aren't actually club info.
**Fix**: Changed to require at least 2 matching fields from `["clubNr", "association", "season", "group_name"]`:
```python
club_info_fields = ["clubNr", "association", "season", "group_name"]
matching_fields = sum(1 for f in club_info_fields if f in block_data)
if matching_fields >= 2:
```

### 4. Added Credential Security Note in Docstring
**Location**: `src/mytt_scraper/utils/in_memory_tables.py:333-338`
**Issue**: Docstring example showed credentials without indicating they should be secure.
**Fix**: Added comment before example:
```python
# Use environment variables or secure vault for credentials
```

## Verification
- Import test passed
- Sample data extraction test passed
- All three backends (polars, pandas, pyarrow) verified working

## Issues Not Fixed
The following items were classified as warnings/suggestions for follow-up tickets:
- No unit tests for extraction logic
- Could add `strict` parameter for debugging
- Could add `include` parameter for selective extraction
- Could expose `Backend` type alias publicly
- Could add `typing.Protocol` for converter function type
