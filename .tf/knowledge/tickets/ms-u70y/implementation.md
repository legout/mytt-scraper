# Implementation: ms-u70y

## Summary

Designed and implemented a backend-agnostic query model for the table viewer with support for filters, sort, and aggregation operations. The implementation includes:

1. **Query Model** (`query_model.py`) - Data structures for query operations
2. **Query Executor** (`query_executor.py`) - Polars executor implementation
3. **Comprehensive Tests** - 81 new tests covering all functionality

## Files Changed

### New Files

- `src/mytt_scraper/utils/query_model.py` - Query model data structures
- `src/mytt_scraper/utils/query_executor.py` - Polars query executor
- `tests/test_query_model.py` - Tests for query model
- `tests/test_query_executor.py` - Tests for query executor

### Modified Files

- `src/mytt_scraper/utils/__init__.py` - Export new modules

## Implementation Details

### Query Model Data Structures

**Enums:**
- `FilterOp` - EQ, NE, GT, GTE, LT, LTE, CONTAINS, STARTS_WITH, ENDS_WITH, IN, IS_NULL, IS_NOT_NULL
- `SortDirection` - ASC, DESC
- `AggFunc` - COUNT, SUM, AVG, MEAN, MIN, MAX, FIRST, LAST

**Dataclasses (frozen/immutable):**
- `Filter(column, op, value)` - Filter condition
- `Sort(column, direction=ASC)` - Sort specification
- `Aggregation(column, func, alias=None)` - Aggregation with auto-generated alias
- `GroupBy(columns, aggregations)` - GroupBy with validation
- `TableSchema(columns)` - Schema for validation
- `Query(filters=[], sort=[], groupby=None, limit=None, offset=None)` - Complete query

### Key Features

1. **Schema Validation**: `Query.validate(schema)` validates all column references
2. **Backend Agnostic**: Query model is independent of execution backend
3. **Type Safe**: Frozen dataclasses with proper typing
4. **Polars Executor**: Full implementation with lazy evaluation
5. **CSV Support**: `execute_csv()` for disk-backed tables via `scan_csv`

### Usage Example

```python
from mytt_scraper.utils.query_model import (
    Query, Filter, FilterOp, Sort, GroupBy, Aggregation, AggFunc, TableSchema
)
from mytt_scraper.utils.query_executor import PolarsQueryExecutor
import polars as pl

# Create a DataFrame
df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "club": ["Berlin", "Munich", "Berlin"],
    "ttr": [1500, 1600, 1550],
})

# Build a query
query = Query(
    filters=[Filter("ttr", FilterOp.GT, 1520)],
    sort=[Sort("name")],
    limit=10
)

# Validate against schema
schema = TableSchema({"name": "string", "club": "string", "ttr": "int"})
is_valid, errors = query.validate(schema)

# Execute
executor = PolarsQueryExecutor()
result = executor.execute(df, query)

# Groupby example
query = Query(
    groupby=GroupBy(
        columns=["club"],
        aggregations=[
            Aggregation("ttr", AggFunc.AVG, alias="avg_ttr"),
            Aggregation("*", AggFunc.COUNT, alias="count")
        ]
    )
)
```

## Tests Run

```bash
uv run pytest tests/test_query_model.py tests/test_query_executor.py -v
```

**Result**: 81 tests passed

Test coverage:
- Filter operations (12 tests)
- Sort operations (3 tests)
- Aggregation (6 tests)
- GroupBy (5 tests)
- TableSchema (7 tests)
- Query validation (13 tests)
- Executor operations (23 tests)
- CSV execution (2 tests)
- Factory function (3 tests)

## Acceptance Criteria

- [x] Define data structures for filters (column, op, value)
- [x] Define data structures for sort (column, direction)
- [x] Define data structures for groupby + aggregations
- [x] Model supports validation against a table schema (column names/types)
- [x] Query model is backend-agnostic (Polars executor first)

## Verification

Run the example in the project:

```bash
cd /Volumes/WD_Blue_1TB/coding/projects/mytt-scraper
uv run python -c "
from mytt_scraper.utils import Query, Filter, FilterOp, Sort, PolarsQueryExecutor
import polars as pl

df = pl.DataFrame({'name': ['Alice', 'Bob'], 'ttr': [1500, 1600]})
query = Query(filters=[Filter('ttr', FilterOp.GT, 1550)])
executor = PolarsQueryExecutor()
result = executor.execute(df, query)
print(result)
"
```
