# Implementation: ms-b2hw

## Summary
Enhanced `TablePreviewScreen` with UI controls for sorting and groupby aggregation operations.

## Files Changed

### `src/mytt_scraper/tui/screens.py`

#### Imports
- Extended imports from `query_model` to include `Sort`, `SortDirection`, `Aggregation`, `AggFunc`, and `GroupBy`

#### Compose Layout
- Restructured query controls into a vertical container with three horizontal panels:
  1. **Filter panel**: Column select, operator select, value input
  2. **Sort panel**: Column select, direction select (ASC/DESC)
  3. **Groupby panel**: Column select, aggregation type select (Count/Sum/Mean/Min/Max)
  4. **Action buttons**: Apply and Reset buttons moved to separate panel

#### New Methods
- `_get_sort_from_ui()`: Builds Sort object from UI inputs
- `_get_groupby_from_ui()`: Builds GroupBy object with Aggregation from UI inputs
- `_apply_query()`: Applies filter, sort, and groupby together in a single query
- `_do_query()`: Background worker that executes combined query operations
- `_reset_query()`: Resets all query controls to defaults and shows base data

#### Updated Methods
- `_update_column_select()`: Now populates column dropdowns for filter, sort, and groupby
- `on_button_pressed()`: Updated to call `_apply_query()` and `_reset_query()`
- `on_worker_state_changed()`: Added handling for `query_worker` with re-enable logic
- `BINDINGS`: Updated action labels ("Apply Query", "Reset All")

## Acceptance Criteria

- [x] Sort: select one column + direction
- [x] Groupby: select 1 column + aggregation type
- [x] Query runs in a worker; results show in DataTable
- [x] Works for both in-memory and disk-backed sources (via existing executor)

## Key Features

### Sort
- Select any column from dropdown
- Choose Ascending or Descending direction
- Applied after filter, before limit

### Groupby Aggregation
- Select column to group by
- Choose aggregation function:
  - **Count**: Count rows per group (uses `*` column)
  - **Sum**: Sum values per group
  - **Mean**: Average values per group
  - **Min**: Minimum value per group
  - **Max**: Maximum value per group
- Results displayed with `{agg}_{column}` naming convention

### Combined Operations
- Filter, Sort, and Groupby can be used independently or together
- Execution order: Filter → Groupby → Sort → Limit
- Background worker keeps UI responsive

## Tests Run

```bash
# Syntax validation
python -m py_compile src/mytt_scraper/tui/screens.py
# Result: Syntax OK

# Query model tests
uv run python -c "
# Tested: Filter only, Sort only, Groupby (count/mean), Combined operations
# All tests passed successfully
"
```

## Verification

To verify the implementation:
1. Run the TUI: `python -m mytt_scraper.tui`
2. Navigate to a table preview screen
3. Verify three panels appear: Filter, Sort, and Group
4. Test sort: select column + direction, click Apply
5. Test groupby: select column + aggregation, click Apply
6. Test combined: set filter + sort + groupby together
7. Test Reset to clear all controls and restore base data
