# Review (Second Opinion): ms-ij43

## Overall Assessment
The implementation successfully adds Textual TUI functionality with a clean three-screen structure (Login, MainMenu, Search) and a working entrypoint. Code is functional and compiles without errors. However, it lacks type hints, exception handling, and follows different documentation patterns than the existing codebase, which could cause maintenance issues as the TUI grows more complex.

## Critical (must fix)
- `src/mytt_scraper/tui/__main__.py:9` - No exception handling around `app.run()`. If the app crashes, the user will see an unfriendly traceback instead of a clean error message. Wrap in try-except block.

- `src/mytt_scraper/tui/screens.py:34-38` - Security issue: Login transition happens regardless of actual authentication. The code transitions to main_menu even though the login is explicitly marked as a placeholder. This gives users false confidence that login succeeded. At minimum add a warning that auth is not implemented.

- `pyproject.toml:10` - Dependency version mismatch: `textual>=0.85.0` specified but implementation.md says Textual 7.5.0 was installed. Version 7.5.0 is actually older than 0.85.0 (Textual had a major version renumbering). Either the version constraint is wrong or the wrong version was installed.

## Major (should fix)
- `src/mytt_scraper/tui/app.py:1-59` - No type hints throughout the file. The rest of the codebase (scraper.py, player_search.py, auth.py) consistently uses type annotations for function parameters and return values. Add type hints to maintain consistency.

- `src/mytt_scraper/tui/screens.py:1-126` - No type hints on methods like `compose()`, `on_button_pressed()`, and action handlers. Other modules have comprehensive type hints.

- `src/mytt_scraper/tui/screens.py:88-89` - Logout in MainMenuScreen only calls `self.app.pop_screen()` without clearing any auth state. When implementing actual auth, this will need to invalidate session/cookies properly.

- `src/mytt_scraper/tui/screens.py:15` - Missing `__all__` export list. Other modules like `utils/__init__.py` and `scraper.py` define `__all__` to explicitly control public API.

## Minor (nice to fix)
- `src/mytt_scraper/tui/app.py:1-59` - Missing `__all__` export list. Should be `__all__ = ["MyttScraperApp"]` to match package conventions.

- `src/mytt_scraper/tui/screens.py:1-126` - Missing `__all__` export list. Should export screen classes: `__all__ = ["LoginScreen", "MainMenuScreen", "SearchScreen"]`.

- `src/mytt_scraper/tui/screens.py:10-44` - Docstrings lack Args/Returns sections. Compare to `auth.py:20-48` which has comprehensive docstrings documenting all parameters and return types.

- `src/mytt_scraper/tui/app.py:1-59` - Class docstring has basic info but could include usage example similar to `scraper.py:20-36`.

- No console script entrypoint in `pyproject.toml`. While `python -m mytt_scraper.tui` works, adding `mytt-scraper-tui = "mytt_scraper.tui.__main__:main"` to `[project.scripts]` would provide a cleaner CLI command.

## Warnings (follow-up ticket)
- `src/mytt_scraper/tui/app.py:18-44` - CSS is embedded as a multi-line string. For larger projects, consider extracting to an external `.css` file for better maintainability and IDE support.

- `src/mytt_scraper/tui/screens.py:115` - Screen names as strings ("login", "main_menu", "search") are used in `app.push_screen()` calls. While correct for Textual, consider defining constants to avoid typos: `LOGIN_SCREEN = "login"`, etc.

- No input sanitization on username/password fields. While Playwright will handle XSS at the browser level, consider adding basic validation (email format for username, minimum length for password) in a future ticket.

## Suggestions (follow-up ticket)
- Consider adding a config screen where users can set preferences (headless mode, default output directory, etc.)

- Add keyboard shortcuts for frequently used actions (e.g., 's' for search, 'f' for fetch profile) in MainMenuScreen to improve power-user experience.

- Consider implementing a result screen to display fetched data (TTR rankings, match history) in a tabular format using Textual's DataTable widget.

- Add proper session management with a SessionManager class that handles login state, cookies, and logout across all screens.

## Positive Notes
- Clean separation of concerns with individual screen classes in `screens.py` and app logic in `app.py`

- Good use of Textual's container widgets (Center, Vertical) for responsive layout

- Consistent naming conventions and clear variable names throughout

- Proper docstrings present on all classes and methods, even if less detailed than other modules

- Good use of Textual's binding system for keyboard shortcuts (q for quit, Ctrl+D for dark mode)

- Placeholder status messages with colored text (red/green/yellow) provide good visual feedback to users

- Back navigation (ESC) and logout (l) bindings follow intuitive UX patterns

## Summary Statistics
- Critical: 3
- Major: 5
- Minor: 5
- Warnings: 3
- Suggestions: 4
