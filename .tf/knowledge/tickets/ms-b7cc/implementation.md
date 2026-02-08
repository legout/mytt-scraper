# Implementation: ms-b7cc

## Summary
Modified `TablePreviewScreen` to accept a `TableProvider` and implemented lazy loading using Polars/PyArrow for efficient table previewing.

## Changes Made

### 1. `src/mytt_scraper/tui/screens.py` - TablePreviewScreen

#### `__init__` method (lines ~1268-1292)
- **Changed signature**: Now accepts `provider: TableProvider` instead of `data`/`csv_path`
- **Updated default limit**: Changed from 500 to 200 rows for better performance
- **Added `_total_rows`**: Track total row count for status display

```python
def __init__(
    self,
    table_name: str,
    provider: TableProvider,
    limit: int = 200,
) -> None:
```

#### `_load_data` method (lines ~1410-1480)
- **Uses TableProvider**: Gets data via `provider.get_data(table_name)`
- **Lazy loading for disk-based tables**: Uses `pl.scan_csv().head().collect()` to avoid loading entire files
- **Supports both sources**: Handles in-memory (Polars/PyArrow) and disk-based (CSV) tables
- **Shows row count**: Returns total row count for status display

#### `_do_query` method (lines ~1753-1803)
- **Handles Path objects**: Reloads from CSV when `_base_data` is a Path (disk-based)
- **Uses total row count**: Reports against `_total_rows` for accurate counts

#### `_do_sql_query` method (lines ~1922-1972)
- **Handles Path objects**: Uses `execute_sql_csv` for disk-based tables
- **Uses total row count**: Reports against `_total_rows`

#### `_reset_query` method (lines ~1804-1854)
- **Handles Path objects**: Reloads from CSV using lazy loading for disk-based tables
- **Shows formatted counts**: Uses comma formatting for large numbers

#### `on_worker_state_changed` method (load_data_worker handler)
- **Updated status message**: Now shows "Showing X of Y rows" format with comma separators

### 2. `src/mytt_scraper/tui/screens.py` - TableListScreen

#### `_open_table` method (lines ~2040-2060)
- **Simplified implementation**: Now passes `TableProvider` directly to `TablePreviewScreen`
- **Removed data extraction**: Preview screen handles lazy loading internally

```python
def _open_table(self, table_name: str) -> None:
    provider = self.app.get_table_provider()
    if not provider.has_table(table_name):
        self.notify(f"Table '{table_name}' not found", severity="error")
        return
    self.app.push_screen(
        TablePreviewScreen(table_name=table_name, provider=provider)
    )
```

## Key Features Implemented

✅ **Accept TableProvider**: Screen now accepts a `TableProvider` for unified table access
✅ **Lazy loading**: Uses `pl.scan_csv().head(N).collect()` for disk-based tables
✅ **Polars/PyArrow support**: Handles both in-memory formats
✅ **Default 200 rows**: Configurable limit, defaults to 200 for performance
✅ **Navigation back**: Preserved existing `action_back` functionality
✅ **Horizontal scroll**: DataTable widget supports this natively
✅ **Row count display**: Shows "Showing X of Y rows" in status

## Files Changed
- `src/mytt_scraper/tui/screens.py` - Modified `TablePreviewScreen` and `TableListScreen`

## Tests Run
```bash
uv run pytest tests/ -v
```
Result: **104 passed in 0.45s**

## Verification
- Syntax check passed: `python3 -m py_compile src/mytt_scraper/tui/screens.py`
- All existing tests continue to pass
- Implementation follows existing code patterns in the codebase
