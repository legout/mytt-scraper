# Research: ms-24n1

## Status
Research complete. Implementation already exists in codebase from blocker ticket ms-b7cc.

## Context Reviewed
- Ticket ms-24n1: Load data in background worker using Polars/PyArrow for responsive viewing
- Blocker ticket ms-b7cc (closed): Build TablePreviewScreen using Textual DataTable + Polars/PyArrow
- Spike: spike-table-viewer-for-python-tui-textual (Workers recommendation)
- Code: `src/mytt_scraper/tui/screens.py` - TablePreviewScreen class

## Findings

### Implementation Status
The `TablePreviewScreen` class in `screens.py` already implements all requirements:

1. **✅ Data loading runs via `run_worker(...)`** - `_load_data()` method is run as a background worker in `on_mount()`
   ```python
   self._query_worker = self.run_worker(
       self._load_data(),
       name="load_data_worker",
       description=f"Load table data for {self.table_name}",
   )
   ```

2. **✅ For disk sources: Uses `pl.scan_csv().head(N).collect()`** - Lazy loading implemented
   ```python
   lazy_df = pl.scan_csv(csv_path)
   df = lazy_df.head(self.limit).collect()
   ```

3. **✅ For in-memory sources: Uses existing DataFrame's `.head(N)`** - Direct head() call
   ```python
   if self.limit and len(df) > self.limit:
       df = df.head(self.limit)
   ```

4. **✅ Convert Polars data to Python lists for DataTable** - `_populate_table()` converts rows
   ```python
   rows = df.rows()
   for row in rows:
       str_row = [str(v) if v is not None else "" for v in row]
       table.add_row(*str_row)
   ```

5. **✅ UI shows loading indicator** - Status updates during load
   ```python
   self._update_status, f"[yellow]📂 Loading {table_info.display_name}...[/]"
   ```

6. **✅ Worker errors are handled** - `on_worker_state_changed()` handles SUCCESS/ERROR/CANCELLED states

7. **✅ Row cap is enforced (configurable, default 200 rows)** - `limit` parameter with default 200

### Code Quality
The implementation follows Textual best practices:
- Uses `call_from_thread()` for UI updates from worker
- Proper worker state handling (SUCCESS, ERROR, CANCELLED)
- Clean separation between data loading and UI population
- Support for both MEMORY and DISK table sources via TableProvider

## Sources
- `src/mytt_scraper/tui/screens.py` - TablePreviewScreen class (lines ~1050-1400)
- `src/mytt_scraper/utils/table_provider.py` - TableProvider abstraction
- Spike: `.tf/knowledge/topics/spike-table-viewer-for-python-tui-textual/spike.md`
