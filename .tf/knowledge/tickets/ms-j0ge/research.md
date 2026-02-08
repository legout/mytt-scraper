# Research: ms-j0ge

## Status
Research enabled. Minimal research performed - implementation approach is clear from existing codebase patterns.

## Context Reviewed
- `tk show ms-j0ge` - Ticket requirements for multi-select + progress screen
- `src/mytt_scraper/tui/screens.py` - Existing SearchScreen implementation
- `src/mytt_scraper/tui/app.py` - TUI app structure
- `src/mytt_scraper/player_search.py` - Reference implementation of `run_search_and_fetch_mode()` with multi-select logic

## Implementation Approach

Based on the existing codebase:

1. **Multi-select in SearchScreen**: 
   - Textual's DataTable supports checkbox columns for multi-selection
   - Add a checkbox column to the results table
   - Track selected user IDs in a list
   - Add "Select All" / "Clear Selection" buttons

2. **Batch Fetch Progress Screen**:
   - Create new `BatchFetchScreen` class
   - Show progress bar (Textual's `ProgressBar` widget)
   - Show current player being fetched
   - Show success/failure count
   - Show scrollable log of per-player results
   - Allow cancel/abort

3. **Error Handling**:
   - Per-player try/except in batch fetch
   - Continue on individual failures
   - Only abort if user explicitly stops

4. **Completion Summary**:
   - Success count, failure count
   - Output directory path
   - List of failed players (if any)

## Textual Widgets to Use
- `DataTable` with checkbox column for multi-select
- `ProgressBar` for overall progress
- `Log` or `RichLog` for per-player status
- `Button` for actions (Start Fetch, Cancel, Back)

## Sources
- Existing codebase patterns (screens.py, player_search.py)
- Textual documentation knowledge (built-in widgets)
