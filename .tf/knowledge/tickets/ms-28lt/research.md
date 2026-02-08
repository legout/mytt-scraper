# Research: ms-28lt

## Status
Research enabled. No additional external research was performed - ticket is straightforward implementation based on existing codebase patterns.

## Context Reviewed

### Ticket Requirements
- Add MainMenuScreen with actions: fetch own profile / fetch by user-id
- Main menu lists actions and routes to the right handler
- Fetch own profile runs and reports success/failure
- Fetch external profile prompts for user-id and runs
- After each action, show a short summary (e.g., tables written to `tables/`)

### Existing Codebase Patterns

#### TUI Structure
- `src/mytt_scraper/tui/app.py` - Main Textual App with reactive scraper state
- `src/mytt_scraper/tui/screens.py` - Screen implementations
  - `LoginScreen` - Background worker pattern for async operations
  - `MainMenuScreen` - Basic structure exists but needs full implementation
  - `SearchScreen` - Placeholder exists

#### Key Patterns from LoginScreen
1. **Background workers** for long-running operations (keeps UI responsive)
2. **Worker state change handlers** for success/failure/cancelled states
3. **Status updates** via `self.app.call_from_thread()` for thread safety
4. **UI disable/enable** during operations
5. **Timer-based navigation** after success

#### Scraper Methods Available
- `scraper.run_own_profile()` - Fetches own profile and saves tables
- `scraper.run_external_profile(user_id)` - Fetches external profile by ID
- `scraper.login()` - Authenticate
- `scraper.tables_dir` - Directory where tables are saved

#### App State Methods
- `app.set_searcher(username, password)` - Creates authenticated scraper
- `app.get_scraper()` - Gets current scraper instance
- `app.is_authenticated()` - Check auth status
- `app.push_screen("name")` / `app.pop_screen()` / `app.switch_screen("name")`

## Implementation Plan

1. **Update MainMenuScreen**:
   - Add proper button handlers for all menu actions
   - Implement fetch own profile with background worker
   - Implement fetch by user-id with input dialog + background worker
   - Show summary after each action (tables written)

2. **Create ResultScreen** (optional) or use notifications:
   - Show summary of what was fetched and where tables were saved

3. **Follow LoginScreen patterns**:
   - Use background workers for scraper operations
   - Update status dynamically
   - Handle errors gracefully

## Files to Modify
- `src/mytt_scraper/tui/screens.py` - Main implementation

## Sources
- `tk show ms-28lt`
- `src/mytt_scraper/tui/screens.py` (existing LoginScreen pattern)
- `src/mytt_scraper/tui/app.py` (app state methods)
- `src/mytt_scraper/scraper.py` (scraper methods)
