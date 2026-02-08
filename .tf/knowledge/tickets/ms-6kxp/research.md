# Research: ms-6kxp

## Status
No external research needed - implementation uses existing codebase patterns.

## Context Reviewed

### Existing PlayerSearcher (src/mytt_scraper/player_search.py)
- `search_players(query, use_playwright=False)` returns `List[Dict[str, Any]]`
- API search by default, Playwright fallback when `use_playwright=True`
- Player dict contains: `user_id`, `name`, `firstname`, `lastname`, `club`, `clubName`, `clubNr`, `ttr`, `personId`

### Current TUI Structure (src/mytt_scraper/tui/)
- `app.py`: Main app with `scraper` reactive state (holds PlayerSearcher instance)
- `screens.py`: 
  - `LoginScreen`: Background worker pattern for async operations
  - `MainMenuScreen`: Navigation with button handlers
  - `SearchScreen`: Placeholder only - needs full implementation
  - `UserIdInputScreen`: Modal for user ID input
  - `ResultScreen`: Result display modal

### Existing Patterns
- Background workers via `self.run_worker()` for async operations
- `on_worker_state_changed()` for handling worker completion
- `DataTable` widget already imported (but not used yet)
- Status updates via `self._update_status()` pattern
- Authentication check via `self.app.is_authenticated()`

## Implementation Plan
1. Enhance SearchScreen with:
   - Search mode toggle (API vs Playwright)
   - Input field with validation
   - DataTable for results (name, club, ttr, user-id columns)
   - Row selection mechanism
   - Background worker for search
   - Navigation to fetch selected user
