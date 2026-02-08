# Implementation: ms-ftgp

## Summary
Added `TablePreviewScreen` - a new TUI screen for previewing tables with a filter panel, apply/reset actions, and background worker support.

## Files Changed

### 1. `src/mytt_scraper/tui/screens.py`
- Added imports for query model and executor
- Added `TablePreviewScreen` class with:
  - Filter panel UI with column Select, operator Select, and value Input
  - Apply and Reset buttons with keyboard shortcuts (a, r)
  - DataTable for displaying results
  - Status area for validation errors and progress
  - Background worker integration for loading data and applying filters
  - Support for both in-memory Polars DataFrames and CSV files
  - Type-aware value conversion (int, float, string)
  - Proper error handling and user feedback

### 2. `src/mytt_scraper/tui/app.py`
- Added `TablePreviewScreen` import
- Added CSS styles for the new screen components
- Registered `table_preview` screen in SCREENS dictionary

## Key Features Implemented

### UI Controls
- **Column Select**: Dropdown populated with available columns from the data source
- **Operator Select**: Dropdown with operators (=, ≠, >, ≥, <, ≤, contains)
- **Value Input**: Text input for filter value
- **Apply Button**: Runs query in background worker
- **Reset Button**: Clears filter and shows base preview

### Background Workers
- **Data Loading**: `load_data_worker` - loads initial data from in-memory or CSV
- **Filter Application**: `filter_worker` - applies filter query using PolarsQueryExecutor

### Validation
- Type-aware value conversion (integers, floats, strings)
- Validation error display in status area
- Invalid type errors shown with clear messages

### Keyboard Shortcuts
- `a` - Apply filter
- `r` - Reset filter
- `escape` - Back to previous screen
- `q` - Quit

## Acceptance Criteria

- [x] UI controls for column + operator + value
- [x] Apply action runs query in a background worker and refreshes DataTable
- [x] Reset action clears query and shows base preview
- [x] Validation errors are shown (invalid column/value/type)

## Tests Run

```bash
# Syntax validation
python -m py_compile src/mytt_scraper/tui/screens.py src/mytt_scraper/tui/app.py
# Result: Syntax OK
```

## Usage Example

```python
from mytt_scraper.tui.screens import TablePreviewScreen
import polars as pl

# With in-memory data
df = pl.DataFrame({"name": ["Alice", "Bob"], "ttr": [1500, 1600]})
app.push_screen(TablePreviewScreen("Player Rankings", data=df))

# With CSV file
app.push_screen(TablePreviewScreen("Player Rankings", csv_path="tables/rankings.csv"))
```

## Verification

To verify the implementation:
1. Run the TUI: `python -m mytt_scraper.tui`
2. Navigate to a screen that opens TablePreviewScreen
3. Verify filter panel appears with column/operator/value controls
4. Test apply with a filter value
5. Verify background worker updates the table
6. Test reset to clear filter
7. Test invalid value (e.g., text in numeric column) shows validation error
