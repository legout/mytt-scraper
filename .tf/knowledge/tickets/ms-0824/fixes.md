# Fixes: ms-0824

## Issues Fixed

### Major Issue 1: execute_csv Missing Validation
**File**: `src/mytt_scraper/utils/query_executor.py`
**Problem**: The `execute_csv` method never invoked schema validation, so `PolarsQueryExecutor(validate=True)` was a no-op for disk-backed tables.

**Fix**: Added validation logic to `execute_csv` that reads the CSV header to build a schema and validates the query before execution. Raises `ValidationError` if validation fails.

```python
# Read header to build schema for validation
if self.validate and has_header:
    from .query_model import TableSchema

    try:
        # Read just the header to get column names
        header_df = pl.read_csv(csv_path, has_header=True, n_rows=0)
        schema = TableSchema({col: str(dtype) for col, dtype in zip(header_df.columns, header_df.dtypes)})
        is_valid, errors = query.validate(schema)
        if not is_valid:
            raise ValidationError(f"Query validation failed: {'; '.join(errors)}")
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        # If we can't read the file for validation, continue and let it fail during execution
        pass
```

### Major Issue 2: Sort Validation Rejected Aggregation Aliases
**File**: `src/mytt_scraper/utils/query_model.py`
**Problem**: Query validation checked sort columns only against the original schema, so queries that group and aggregate then sort by an aggregation alias (e.g., `avg_ttr`) were incorrectly rejected.

**Fix**: Modified the sort validation to include aggregation aliases as valid sort columns when a groupby is present.

```python
# Validate sort columns
# When groupby is present, sort can reference aggregation aliases
valid_sort_columns = set(schema.columns.keys())
if self.groupby:
    # Add aggregation aliases as valid sort columns
    for agg in self.groupby.aggregations:
        valid_sort_columns.add(agg.alias)

for s in self.sort:
    if s.column not in valid_sort_columns:
        errors.append(f"Sort references unknown column: {s.column}")
```

## Test Results After Fixes
```
uv run pytest tests/test_query_model.py tests/test_query_executor.py -v
============================== 81 passed in 0.24s ==============================
```

## Files Changed
- `src/mytt_scraper/utils/query_executor.py` - Added validation to `execute_csv`
- `src/mytt_scraper/utils/query_model.py` - Fixed sort validation to include aggregation aliases
