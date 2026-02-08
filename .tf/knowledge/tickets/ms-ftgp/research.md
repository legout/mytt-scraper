# Research: ms-ftgp

## Status
Research enabled. No additional external research was performed.

## Rationale
- This is a straightforward UI implementation ticket building on existing infrastructure
- Query model (query_model.py) and executor (query_executor.py) are already implemented (ticket ms-0824)
- TUI framework (Textual) is already established with existing screens
- Pattern can be followed from existing screens like SearchScreen and BatchFetchScreen

## Context Reviewed
- `tk show ms-ftgp` - Ticket requirements for filter panel UI
- `src/mytt_scraper/utils/query_model.py` - Filter, Sort, Query classes with validation
- `src/mytt_scraper/utils/query_executor.py` - PolarsQueryExecutor for query execution
- `src/mytt_scraper/tui/screens.py` - Existing screen patterns with workers
- `src/mytt_scraper/tui/app.py` - App structure and screen registration
- `.tf/knowledge/topics/seed-add-filters-and-advanced-queries-to-the/` - Seed context
- `.tf/knowledge/topics/spike-table-viewer-for-python-tui-textual/` - Textual DataTable patterns

## Implementation Plan
1. Create TablePreviewScreen with DataTable display
2. Add FilterPanel widget (or inline) with:
   - Column selection dropdown
   - Operator selection (equals, contains, >, >=, <, <=)
   - Value input field
3. Implement Apply/Reset actions
4. Use background workers for query execution (following BatchFetchScreen pattern)
5. Show validation errors in status area
6. Register screen in app.py

## Sources
- (none - using existing codebase patterns)
