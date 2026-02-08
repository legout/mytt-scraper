# Research: ms-08nr

## Status
Research enabled. No additional external research was performed - this is a straightforward documentation task based on existing codebase.

## Context Reviewed
- `tk show ms-08nr` - Ticket requirements
- `README.md` - Existing project documentation
- `src/mytt_scraper/tui/__main__.py` - TUI entry point
- `src/mytt_scraper/tui/app.py` - TUI app structure
- `src/mytt_scraper/tui/screens.py` - All TUI screens and features

## Key Findings

### TUI Entry Point
```bash
python -m mytt_scraper.tui
```

### TUI Features (from screens.py)
1. **LoginScreen** - Username/password login with background worker
2. **MainMenuScreen** - Menu with: Fetch My Profile, Search Players, Fetch by User ID
3. **SearchScreen** - Player search with API/Playwright toggle, multi-select, batch fetch
4. **BatchFetchScreen** - Progress tracking for fetching multiple players
5. **UserIdInputScreen** - Modal for entering user ID
6. **ResultScreen** - Shows fetch results summary

### Headless Mode
- TUI always runs browser in headless mode (hardcoded in screens.py)
- Headed mode not currently supported in TUI (different from CLI scripts)

### Supported Workflows
1. Login with credentials
2. Fetch own profile data
3. Search for players by name (API or Playwright mode)
4. Select multiple players from search results
5. Batch fetch selected players
6. Fetch by specific user ID

## Sources
- (none - internal codebase only)
