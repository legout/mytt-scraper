# Implementation: ms-0824

## Summary
The Polars query executor was already fully implemented in the codebase. This ticket required implementing a query executor that applies the query model to in-memory Polars DataFrames and disk-backed CSV tables via `pl.scan_csv()` / `pl.read_csv()`.

## Files Changed
- No changes required - implementation already complete

## Implementation Details

The following components were already implemented:

### 1. Query Model (`src/mytt_scraper/utils/query_model.py`)
- **Filter**: Support for all filter operators (EQ, NE, GT, GTE, LT, LTE, CONTAINS, STARTS_WITH, ENDS_WITH, IN, IS_NULL, IS_NOT_NULL)
- **Sort**: Single and multi-column sorting with ASC/DESC directions
- **Aggregation**: All aggregation functions (COUNT, SUM, AVG, MEAN, MIN, MAX, FIRST, LAST)
- **GroupBy**: Multi-column grouping with multiple aggregations
- **TableSchema**: Schema validation for queries
- **Query**: Complete query specification with filters, sort, groupby, limit, and offset

### 2. Query Executor (`src/mytt_scraper/utils/query_executor.py`)
- **PolarsQueryExecutor**: Main executor class with:
  - `execute(df, query)`: Execute queries against in-memory DataFrames
  - `execute_csv(path, query)`: Execute queries against CSV files using lazy scanning
  - Full lazy evaluation support via `pl.LazyFrame`
  - Validation support (optional)
  - All filter operators implemented
  - Sort, groupby, limit, and offset support
- **create_executor()**: Factory function for creating executor instances

## Acceptance Criteria Verification

| Criteria | Status | Notes |
|----------|--------|-------|
| Executor can load data from a TableProvider | ✅ | Supported via `execute()` for DataFrames and `execute_csv()` for disk files |
| Applies filters (==, contains, >, >=, <, <=) | ✅ | All filter operators implemented and tested |
| Applies sort (single column) | ✅ | Single and multi-column sort supported |
| Applies groupby + basic aggregations | ✅ | count, sum, mean, min, max, first, last supported |
| Uses lazy operations and collects head(N) | ✅ | Uses `pl.LazyFrame` throughout, only collects at end |
| Returns Polars DataFrame for DataTable display | ✅ | Returns `pl.DataFrame` |

## Tests Run

```bash
uv run pytest tests/test_query_model.py tests/test_query_executor.py -v
```

**Result**: 81 passed in 0.22s

All tests pass including:
- Filter operations (EQ, NE, GT, GTE, LT, LTE, CONTAINS, STARTS_WITH, ENDS_WITH, IN, IS_NULL, IS_NOT_NULL)
- Sort operations (ASC, DESC, multi-column)
- GroupBy with aggregations (COUNT, SUM, AVG, MIN, MAX)
- Limit and offset
- Complex queries combining all operations
- CSV execution via scan_csv
- Validation and error handling

## Verification

The implementation can be verified by running:

```python
import polars as pl
from mytt_scraper.utils.query_model import Query, Filter, FilterOp, Sort, SortDirection
from mytt_scraper.utils.query_executor import PolarsQueryExecutor

# Create sample data
df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "ttr": [1500, 1600, 1550],
    "club": ["Berlin", "Munich", "Berlin"]
})

# Execute query
executor = PolarsQueryExecutor()
query = Query(
    filters=[Filter("ttr", FilterOp.GT, 1520)],
    sort=[Sort("name", SortDirection.ASC)]
)
result = executor.execute(df, query)
```

## Key Design Decisions

1. **Lazy Evaluation**: All operations use Polars lazy API (`pl.LazyFrame`) for optimization
2. **Validation**: Optional schema validation to catch errors early
3. **Backend Agnostic**: Query model is separate from execution backend
4. **CSV Support**: Direct support for disk-backed tables via `scan_csv` without full load
5. **Error Handling**: Custom exceptions (`QueryExecutorError`, `ValidationError`) for clear error messages
