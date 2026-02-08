"""TUI Screens for mytt-scraper."""

from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Center, Vertical, Horizontal
from textual.screen import Screen, ModalScreen
from textual.widgets import (
    Button, Footer, Header, Input, Label, Static, DataTable,
    Switch, Checkbox, ProgressBar, RichLog, Select
)
from textual.worker import Worker

from ..utils.auth import login_with_playwright
from ..utils.query_model import Filter, FilterOp, Query, Sort, SortDirection
from ..utils.query_executor import PolarsQueryExecutor, ValidationError, QueryExecutorError

__all__ = [
    "LoginScreen", "MainMenuScreen", "SearchScreen",
    "UserIdInputScreen", "ResultScreen", "BatchFetchScreen",
    "TablePreviewScreen"
]


class LoginScreen(Screen):
    """Screen for user login with username/password.
    
    Login runs in a background worker to keep the UI responsive.
    Credentials are session-only (not persisted).
    """

    BINDINGS = [("q", "quit", "Quit")]
    
    def __init__(self) -> None:
        super().__init__()
        self._login_worker: Worker | None = None
        self._username: str = ""
        self._password: str = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="login-container"):
            yield Label("MyTischtennis Login", id="login-title")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            with Center():
                yield Button("Login", id="login-btn", variant="primary")
            yield Static("Enter credentials to continue", id="login-status")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle login button press."""
        if event.button.id == "login-btn":
            self._start_login()
    
    def _start_login(self) -> None:
        """Validate inputs and start background login worker."""
        username_input = self.query_one("#username", Input)
        password_input = self.query_one("#password", Input)
        login_btn = self.query_one("#login-btn", Button)
        status = self.query_one("#login-status", Static)
        
        self._username = username_input.value.strip()
        self._password = password_input.value
        
        if not self._username or not self._password:
            status.update("[red]Please enter both username and password[/]")
            return
        
        # Disable inputs and button during login
        username_input.disabled = True
        password_input.disabled = True
        login_btn.disabled = True
        login_btn.label = "Logging in..."
        
        # Update status
        status.update("[yellow]🔄 Starting login process...[/]")
        
        # Run login in background worker to keep UI responsive
        self._login_worker = self.run_worker(
            self._do_login(self._username, self._password),
            name="login_worker",
            description="Login to mytischtennis.de",
        )
    
    async def _do_login(self, username: str, password: str) -> bool:
        """Background worker task to perform login via Playwright.
        
        Args:
            username: Email/username for login
            password: Password for login
            
        Returns:
            True if login successful, False otherwise
        """
        # Update status via app call_from_thread for thread safety
        self.app.call_from_thread(
            self._update_status, "[yellow]🌐 Connecting to mytischtennis.de...[/]"
        )
        
        try:
            # Run the async login function
            result = await login_with_playwright(username, password, headless=True)
            return result
        except Exception as e:
            # Log error and return failure
            self.app.call_from_thread(
                self._update_status, f"[red]❌ Error during login: {e}[/]"
            )
            return False
    
    def _update_status(self, message: str) -> None:
        """Update the status display.
        
        Args:
            message: Status message to display
        """
        status = self.query_one("#login-status", Static)
        status.update(message)
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes (completion, error, etc.).
        
        Args:
            event: Worker state change event
        """
        if event.worker.name != "login_worker":
            return
        
        if event.state == Worker.State.SUCCESS:
            # Login completed, check result
            result = event.worker.result
            if result:
                self._handle_login_success()
            else:
                self._handle_login_failure("Login failed. Please check your credentials.")
        elif event.state == Worker.State.ERROR:
            # Worker encountered an error
            error_msg = str(event.worker.error) if event.worker.error else "Unknown error"
            self._handle_login_failure(f"Login error: {error_msg}")
        elif event.state == Worker.State.CANCELLED:
            # Worker was cancelled
            self._handle_login_failure("Login was cancelled.")
    
    def _handle_login_success(self) -> None:
        """Handle successful login - store scraper and navigate to main menu."""
        status = self.query_one("#login-status", Static)
        status.update("[green]✓ Login successful![/]")
        
        # Create and store authenticated scraper in app state
        # Using PlayerSearcher which extends MyTischtennisScraper
        self.app.set_searcher(self._username, self._password, headless=True)
        
        # Clear credentials from memory (session-only)
        self._password = ""
        
        # Navigate to main menu after brief delay to show success
        self.set_timer(0.5, lambda: self.app.push_screen("main_menu"))
    
    def _handle_login_failure(self, message: str) -> None:
        """Handle login failure - show error and allow retry.
        
        Args:
            message: Error message to display
        """
        status = self.query_one("#login-status", Static)
        status.update(f"[red]❌ {message}[/]")
        
        # Re-enable inputs and button for retry
        self._enable_login_form()
    
    def _enable_login_form(self) -> None:
        """Re-enable the login form for retry."""
        username_input = self.query_one("#username", Input)
        password_input = self.query_one("#password", Input)
        login_btn = self.query_one("#login-btn", Button)
        
        username_input.disabled = False
        password_input.disabled = False
        login_btn.disabled = False
        login_btn.label = "Login"
        
        # Clear password for security
        password_input.value = ""
        self._password = ""
    
    def action_quit(self) -> None:
        """Quit the application."""
        # Cancel any running login worker
        if self._login_worker and self._login_worker.is_running:
            self._login_worker.cancel()
        self.app.exit()


class MainMenuScreen(Screen):
    """Main menu screen with navigation to all features.

    Supports fetching own profile and fetching external profiles by user ID,
    with background workers to keep the UI responsive.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("l", "logout", "Logout"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._fetch_worker: Worker | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="menu-container"):
            yield Label("Main Menu", id="menu-title")
            yield Static("Select an action to continue", id="menu-status")
            with Center():
                yield Button("Fetch My Profile", id="fetch-profile", variant="primary")
            with Center():
                yield Button("Search Players", id="search-players")
            with Center():
                yield Button("Fetch by User ID", id="fetch-by-id")
        yield Footer()

    def on_mount(self) -> None:
        """Check authentication on mount."""
        if not self.app.is_authenticated():
            self.notify("Not authenticated. Please login.", severity="error")
            self.app.switch_screen("login")

    def _update_status(self, message: str) -> None:
        """Update the status display.

        Args:
            message: Status message to display
        """
        status = self.query_one("#menu-status", Static)
        status.update(message)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable all menu buttons.

        Args:
            enabled: True to enable, False to disable
        """
        for button_id in ["fetch-profile", "search-players", "fetch-by-id"]:
            button = self.query_one(f"#{button_id}", Button)
            button.disabled = not enabled

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu button presses."""
        button_id = event.button.id

        if button_id == "fetch-profile":
            self._start_fetch_own_profile()
        elif button_id == "search-players":
            self.app.push_screen("search")
        elif button_id == "fetch-by-id":
            self._show_user_id_input()

    def _start_fetch_own_profile(self) -> None:
        """Start fetching the user's own profile in a background worker."""
        scraper = self.app.get_scraper()
        if not scraper:
            self.notify("Not authenticated", severity="error")
            return

        # Disable buttons during operation
        self._set_buttons_enabled(False)
        self._update_status("[yellow]🔄 Fetching your profile...[/]")

        # Run fetch in background worker
        self._fetch_worker = self.run_worker(
            self._do_fetch_own_profile(scraper),
            name="fetch_profile_worker",
            description="Fetch own profile data",
        )

    async def _do_fetch_own_profile(self, scraper) -> dict:
        """Background worker to fetch own profile.

        Args:
            scraper: Authenticated scraper instance

        Returns:
            Dictionary with success status and result info
        """
        self.app.call_from_thread(
            self._update_status, "[yellow]🌐 Logging in and fetching data...[/]"
        )

        try:
            # Login first
            if not scraper.login():
                return {"success": False, "error": "Login failed"}

            self.app.call_from_thread(
                self._update_status, "[yellow]📊 Extracting tables...[/]"
            )

            # Fetch own profile data
            data = scraper.run_own_profile()

            if data:
                # Get list of tables that were written
                tables_dir = scraper.tables_dir
                tables_written = self._get_tables_written(tables_dir)

                return {
                    "success": True,
                    "type": "own_profile",
                    "tables_dir": str(tables_dir),
                    "tables_written": tables_written,
                }
            else:
                return {"success": False, "error": "Failed to fetch profile data"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _show_user_id_input(self) -> None:
        """Show the user ID input modal screen."""
        self.app.push_screen(UserIdInputScreen(), callback=self._on_user_id_entered)

    def _on_user_id_entered(self, user_id: str | None) -> None:
        """Handle user ID input from modal.

        Args:
            user_id: The entered user ID, or None if cancelled
        """
        if not user_id:
            return  # User cancelled

        scraper = self.app.get_scraper()
        if not scraper:
            self.notify("Not authenticated", severity="error")
            return

        # Disable buttons during operation
        self._set_buttons_enabled(False)
        self._update_status(f"[yellow]🔄 Fetching profile for user: {user_id}...[/]")

        # Run fetch in background worker
        self._fetch_worker = self.run_worker(
            self._do_fetch_external_profile(scraper, user_id),
            name="fetch_external_worker",
            description=f"Fetch external profile: {user_id}",
        )

    async def _do_fetch_external_profile(self, scraper, user_id: str) -> dict:
        """Background worker to fetch external profile.

        Args:
            scraper: Authenticated scraper instance
            user_id: User ID to fetch

        Returns:
            Dictionary with success status and result info
        """
        self.app.call_from_thread(
            self._update_status, "[yellow]🌐 Logging in and fetching data...[/]"
        )

        try:
            # Login first
            if not scraper.login():
                return {"success": False, "error": "Login failed"}

            self.app.call_from_thread(
                self._update_status, f"[yellow]📊 Fetching profile for {user_id}...[/]"
            )

            # Fetch external profile data
            data = scraper.run_external_profile(user_id)

            if data:
                # Get list of tables that were written
                tables_dir = scraper.tables_dir
                tables_written = self._get_tables_written(tables_dir, prefix=f"{user_id}_")

                return {
                    "success": True,
                    "type": "external_profile",
                    "user_id": user_id,
                    "tables_dir": str(tables_dir),
                    "tables_written": tables_written,
                }
            else:
                return {"success": False, "error": "Failed to fetch profile data"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_tables_written(self, tables_dir: Path, prefix: str = "") -> list[str]:
        """Get list of CSV files written to tables directory.

        Args:
            tables_dir: Directory where tables are stored
            prefix: Optional filename prefix to filter by

        Returns:
            List of filenames
        """
        if not tables_dir.exists():
            return []

        files = []
        for f in tables_dir.iterdir():
            if f.is_file() and f.suffix == ".csv":
                if not prefix or f.name.startswith(prefix):
                    files.append(f.name)

        return sorted(files)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes for fetch operations.

        Args:
            event: Worker state change event
        """
        if event.worker.name not in ["fetch_profile_worker", "fetch_external_worker"]:
            return

        if event.state == Worker.State.SUCCESS:
            result = event.worker.result
            if result and result.get("success"):
                self._handle_fetch_success(result)
            else:
                error = result.get("error", "Unknown error") if result else "Unknown error"
                self._handle_fetch_failure(error)
        elif event.state == Worker.State.ERROR:
            error_msg = str(event.worker.error) if event.worker.error else "Unknown error"
            self._handle_fetch_failure(error_msg)
        elif event.state == Worker.State.CANCELLED:
            self._handle_fetch_failure("Operation was cancelled")

    def _handle_fetch_success(self, result: dict) -> None:
        """Handle successful fetch operation.

        Args:
            result: Result dictionary from fetch operation
        """
        self._update_status("[green]✓ Fetch completed successfully![/]")

        # Show result screen with summary
        self.app.push_screen(ResultScreen(result))

        # Re-enable buttons
        self._set_buttons_enabled(True)

    def _handle_fetch_failure(self, message: str) -> None:
        """Handle fetch failure.

        Args:
            message: Error message to display
        """
        self._update_status(f"[red]❌ {message}[/]")
        self.notify(f"Fetch failed: {message}", severity="error")

        # Re-enable buttons for retry
        self._set_buttons_enabled(True)

    def action_logout(self) -> None:
        """Logout and return to login screen."""
        # Cancel any running worker
        if self._fetch_worker and self._fetch_worker.is_running:
            self._fetch_worker.cancel()
        self.app.clear_scraper()
        self.app.switch_screen("login")


class SearchScreen(Screen):
    """Screen for searching players with API/Playwright toggle and multi-select results.

    Features:
    - Search mode toggle (API vs Playwright)
    - Results displayed in a DataTable with checkboxes for multi-select
    - Multi-select support for batch fetching
    - Background worker for non-blocking search
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
        ("space", "toggle_selection", "Toggle Select"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._search_worker: Worker | None = None
        self._search_results: list[dict] = []
        self._selected_user_ids: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="search-container"):
            yield Label("Search Players", id="search-title")

            # Search input and mode toggle
            yield Input(placeholder="Search by name...", id="search-input")
            with Horizontal(id="search-options"):
                yield Label("Use Playwright:", id="playwright-label")
                yield Switch(id="playwright-toggle", value=False)
                yield Static("(API mode)", id="mode-indicator")

            with Center():
                yield Button("Search", id="search-btn", variant="primary")

            yield Static("Enter a name to search", id="search-status")

            # Selection controls (hidden until results)
            with Horizontal(id="selection-controls"):
                yield Button("Select All", id="select-all-btn", disabled=True)
                yield Button("Clear Selection", id="clear-selection-btn", disabled=True)
                yield Static("0 selected", id="selection-count")

            # Results table (initially hidden/empty)
            yield DataTable(id="results-table")

            # Fetch button
            with Center():
                yield Button(
                    "Fetch Selected Players", 
                    id="fetch-btn", 
                    variant="success", 
                    disabled=True
                )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the results table."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("✓", "Name", "Club", "TTR", "User ID")
        table.cursor_type = "row"
        table.disabled = True  # Disabled until we have results

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle search mode toggle."""
        if event.switch.id == "playwright-toggle":
            indicator = self.query_one("#mode-indicator", Static)
            if event.value:
                indicator.update("(Playwright mode)")
            else:
                indicator.update("(API mode)")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "search-btn":
            self._start_search()
        elif event.button.id == "select-all-btn":
            self._select_all()
        elif event.button.id == "clear-selection-btn":
            self._clear_selection()
        elif event.button.id == "fetch-btn":
            self._start_batch_fetch()

    def _start_search(self) -> None:
        """Validate inputs and start background search worker."""
        query_input = self.query_one("#search-input", Input)
        search_btn = self.query_one("#search-btn", Button)
        status = self.query_one("#search-status", Static)
        table = self.query_one("#results-table", DataTable)
        use_playwright = self.query_one("#playwright-toggle", Switch).value

        query = query_input.value.strip()

        if not query:
            status.update("[red]Please enter a search term[/]")
            return

        # Check authentication
        if not self.app.is_authenticated():
            status.update("[red]Not authenticated. Please login first.[/]")
            return

        # Disable controls during search
        query_input.disabled = True
        search_btn.disabled = True
        search_btn.label = "Searching..."

        # Clear previous results
        table.clear()
        table.disabled = True
        self._search_results = []
        self._selected_user_ids.clear()
        self._update_selection_ui()

        mode_text = "Playwright" if use_playwright else "API"
        status.update(f"[yellow]🔄 Searching via {mode_text} for '{query}'...[/]")

        # Run search in background worker
        scraper = self.app.get_scraper()
        self._search_worker = self.run_worker(
            self._do_search(scraper, query, use_playwright),
            name="search_worker",
            description=f"Search for players: {query}",
        )

    async def _do_search(self, scraper, query: str, use_playwright: bool) -> list[dict]:
        """Background worker to perform player search.

        Args:
            scraper: Authenticated scraper instance (PlayerSearcher)
            query: Search query string
            use_playwright: Whether to use Playwright mode

        Returns:
            List of player dictionaries
        """
        try:
            # PlayerSearcher has search_players method
            if hasattr(scraper, 'search_players'):
                results = scraper.search_players(query, use_playwright=use_playwright)
                return results
            else:
                return []
        except Exception as e:
            self.app.call_from_thread(
                self._update_status, f"[red]Search error: {e}[/]"
            )
            return []

    def _update_status(self, message: str) -> None:
        """Update the status display."""
        status = self.query_one("#search-status", Static)
        status.update(message)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle search worker completion."""
        if event.worker.name != "search_worker":
            return

        if event.state == Worker.State.SUCCESS:
            results = event.worker.result or []
            self._handle_search_success(results)
        elif event.state == Worker.State.ERROR:
            error_msg = str(event.worker.error) if event.worker.error else "Unknown error"
            self._handle_search_failure(f"Search error: {error_msg}")
        elif event.state == Worker.State.CANCELLED:
            self._handle_search_failure("Search was cancelled")

    def _handle_search_success(self, results: list[dict]) -> None:
        """Handle successful search - populate results table."""
        self._search_results = results
        status = self.query_one("#search-status", Static)
        table = self.query_one("#results-table", DataTable)

        if not results:
            status.update("[yellow]No players found[/]")
            table.disabled = True
            self._set_selection_controls_enabled(False)
        else:
            status.update(f"[green]✓ Found {len(results)} player(s)[/]")
            table.disabled = False
            self._set_selection_controls_enabled(True)

            # Populate table
            for player in results:
                # Build display name
                name = player.get('name', '')
                if not name:
                    firstname = player.get('firstname', player.get('firstName', ''))
                    lastname = player.get('lastname', player.get('lastName', ''))
                    name = f"{firstname} {lastname}".strip()

                club = player.get('club', player.get('clubName', 'N/A'))
                ttr = str(player.get('ttr', 'N/A'))
                user_id = player.get('user_id', player.get('personId', 'N/A'))

                # Checkbox column shows "☐" or "☑" based on selection
                checkbox = "☐"
                table.add_row(checkbox, name, club, ttr, user_id, key=user_id)

        # Re-enable controls
        self._enable_search_form()

    def _handle_search_failure(self, message: str) -> None:
        """Handle search failure."""
        self._update_status(f"[red]❌ {message}[/]")
        self._enable_search_form()
        self._set_selection_controls_enabled(False)

    def _enable_search_form(self) -> None:
        """Re-enable search form controls."""
        query_input = self.query_one("#search-input", Input)
        search_btn = self.query_one("#search-btn", Button)

        query_input.disabled = False
        search_btn.disabled = False
        search_btn.label = "Search"

    def _set_selection_controls_enabled(self, enabled: bool) -> None:
        """Enable or disable selection control buttons."""
        select_all_btn = self.query_one("#select-all-btn", Button)
        clear_selection_btn = self.query_one("#clear-selection-btn", Button)
        
        select_all_btn.disabled = not enabled
        clear_selection_btn.disabled = not enabled

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in results table - toggle checkbox."""
        user_id = event.row_key.value
        if not user_id:
            return

        table = self.query_one("#results-table", DataTable)
        
        # Toggle selection
        if user_id in self._selected_user_ids:
            self._selected_user_ids.discard(user_id)
        else:
            self._selected_user_ids.add(user_id)

        # Update the checkbox display for this row
        self._update_row_checkbox(table, user_id)
        self._update_selection_ui()

    def action_toggle_selection(self) -> None:
        """Toggle selection of the currently highlighted row."""
        table = self.query_one("#results-table", DataTable)
        if table.cursor_row is None:
            return
        
        # Get the row key at cursor position
        row_key = table.get_row_at(table.cursor_row)
        if row_key and len(row_key) > 4:
            user_id = row_key[4]  # User ID is in the 5th column
            
            # Toggle selection
            if user_id in self._selected_user_ids:
                self._selected_user_ids.discard(user_id)
            else:
                self._selected_user_ids.add(user_id)
            
            self._update_row_checkbox(table, user_id)
            self._update_selection_ui()

    def _update_row_checkbox(self, table: DataTable, user_id: str) -> None:
        """Update the checkbox display for a specific row."""
        # Get current row data
        row = table.get_row(user_id)
        if row:
            checkbox = "☑" if user_id in self._selected_user_ids else "☐"
            # Update the row with new checkbox state
            new_row = (checkbox,) + row[1:]
            table.update_cell(user_id, table.columns[0].key, checkbox)

    def _select_all(self) -> None:
        """Select all players in the results."""
        table = self.query_one("#results-table", DataTable)
        
        for player in self._search_results:
            user_id = player.get('user_id', player.get('personId', ''))
            if user_id:
                self._selected_user_ids.add(user_id)
                self._update_row_checkbox(table, user_id)
        
        self._update_selection_ui()

    def _clear_selection(self) -> None:
        """Clear all selections."""
        table = self.query_one("#results-table", DataTable)
        
        for user_id in list(self._selected_user_ids):
            self._update_row_checkbox(table, user_id)
        
        self._selected_user_ids.clear()
        self._update_selection_ui()

    def _update_selection_ui(self) -> None:
        """Update selection count display and fetch button state."""
        count_label = self.query_one("#selection-count", Static)
        fetch_btn = self.query_one("#fetch-btn", Button)
        
        count = len(self._selected_user_ids)
        count_label.update(f"{count} selected")
        fetch_btn.disabled = count == 0
        
        if count > 0:
            fetch_btn.label = f"Fetch {count} Player{'s' if count > 1 else ''}"
        else:
            fetch_btn.label = "Fetch Selected Players"

    def _start_batch_fetch(self) -> None:
        """Start batch fetch for selected players."""
        if not self._selected_user_ids:
            self.notify("No players selected", severity="warning")
            return

        # Get player info for selected users
        selected_players = []
        for player in self._search_results:
            user_id = player.get('user_id', player.get('personId', ''))
            if user_id in self._selected_user_ids:
                selected_players.append(player)

        # Push the batch fetch screen
        self.app.push_screen(BatchFetchScreen(selected_players))

    def action_back(self) -> None:
        """Return to main menu."""
        # Cancel any running worker
        if self._search_worker and self._search_worker.is_running:
            self._search_worker.cancel()
        self.app.pop_screen()


class BatchFetchScreen(Screen):
    """Screen for batch fetching multiple player profiles with progress tracking.

    Features:
    - Progress bar showing overall completion
    - Per-player status log
    - Error handling without aborting
    - Completion summary with success/failure counts
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "cancel", "Cancel"),
        ("c", "cancel", "Cancel Fetch"),
    ]

    def __init__(self, players: list[dict]) -> None:
        super().__init__()
        self._players = players
        self._fetch_worker: Worker | None = None
        self._cancelled = False
        self._results: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="batch-fetch-container"):
            yield Label("Batch Fetch Progress", id="batch-fetch-title")
            
            # Progress section
            with Vertical(id="progress-section"):
                yield Static(
                    f"Fetching {len(self._players)} player(s)...", 
                    id="progress-status"
                )
                yield ProgressBar(
                    total=len(self._players),
                    show_eta=False,
                    id="progress-bar"
                )
            
            # Stats section
            with Horizontal(id="stats-section"):
                yield Static("✓ Success: 0", id="success-count", classes="stat")
                yield Static("✗ Failed: 0", id="failure-count", classes="stat")
                yield Static("⏳ Remaining: 0", id="remaining-count", classes="stat")
            
            # Log of per-player results
            yield Label("Fetch Log:", id="log-label")
            yield RichLog(id="fetch-log", highlight=True, markup=True)
            
            # Action buttons
            with Center():
                yield Button(
                    "Cancel", 
                    id="cancel-btn", 
                    variant="error"
                )
                yield Button(
                    "Back to Search", 
                    id="back-btn", 
                    variant="primary",
                    disabled=True
                )

        yield Footer()

    def on_mount(self) -> None:
        """Start batch fetch when screen mounts."""
        self._update_stats()
        self._start_batch_fetch()

    def _start_batch_fetch(self) -> None:
        """Start the background worker for batch fetching."""
        scraper = self.app.get_scraper()
        if not scraper:
            self._log_message("[red]❌ Not authenticated[/]")
            return

        self._fetch_worker = self.run_worker(
            self._do_batch_fetch(scraper),
            name="batch_fetch_worker",
            description=f"Batch fetch {len(self._players)} players",
        )

    async def _do_batch_fetch(self, scraper) -> dict:
        """Background worker to fetch all selected players sequentially.

        Args:
            scraper: Authenticated scraper instance

        Returns:
            Dictionary with summary statistics
        """
        success_count = 0
        failure_count = 0
        failed_players: list[tuple[str, str]] = []
        tables_dir = scraper.tables_dir if hasattr(scraper, 'tables_dir') else Path("tables")

        # Ensure logged in
        self.app.call_from_thread(
            self._log_message, "[yellow]🔐 Logging in...[/]"
        )
        
        try:
            if hasattr(scraper, 'login') and not scraper.login():
                self.app.call_from_thread(
                    self._log_message, "[red]❌ Login failed[/]"
                )
                return {
                    "success": False,
                    "error": "Login failed",
                    "success_count": 0,
                    "failure_count": len(self._players),
                }
        except Exception as e:
            self.app.call_from_thread(
                self._log_message, f"[red]❌ Login error: {e}[/]"
            )
            return {
                "success": False,
                "error": str(e),
                "success_count": 0,
                "failure_count": len(self._players),
            }

        self.app.call_from_thread(
            self._log_message, "[green]✓ Logged in successfully[/]"
        )

        # Fetch each player
        for i, player in enumerate(self._players, 1):
            if self._cancelled:
                self.app.call_from_thread(
                    self._log_message, "[yellow]⚠ Fetch cancelled by user[/]"
                )
                break

            user_id = player.get('user_id', player.get('personId', ''))
            name = self._get_player_name(player)

            # Update progress
            self.app.call_from_thread(
                self._update_progress, i - 1, name
            )

            # Log start
            self.app.call_from_thread(
                self._log_message, f"[{i}/{len(self._players)}] Fetching: [bold]{name}[/] ({user_id})"
            )

            try:
                # Fetch the player
                if hasattr(scraper, 'run_external_profile'):
                    data = scraper.run_external_profile(user_id)
                    
                    if data:
                        success_count += 1
                        self.app.call_from_thread(
                            self._log_message, 
                            f"  [green]✓ Success[/] - Data fetched for {name}"
                        )
                    else:
                        failure_count += 1
                        failed_players.append((name, "No data returned"))
                        self.app.call_from_thread(
                            self._log_message, 
                            f"  [red]✗ Failed[/] - No data for {name}"
                        )
                else:
                    failure_count += 1
                    failed_players.append((name, "Scraper doesn't support external profile"))
                    self.app.call_from_thread(
                        self._log_message, 
                        f"  [red]✗ Failed[/] - Scraper doesn't support external profile fetch"
                    )

            except Exception as e:
                failure_count += 1
                failed_players.append((name, str(e)))
                self.app.call_from_thread(
                    self._log_message, 
                    f"  [red]✗ Error[/] - {name}: {e}"
                )

            # Small delay between requests to be polite
            if i < len(self._players) and not self._cancelled:
                import asyncio
                await asyncio.sleep(0.5)

            # Update stats
            self.app.call_from_thread(
                self._update_stats, success_count, failure_count, 
                len(self._players) - i
            )

        # Complete progress bar
        self.app.call_from_thread(
            self._update_progress, 
            success_count + failure_count, 
            "Complete"
        )

        # Log summary
        self.app.call_from_thread(
            self._log_message, 
            f"\n[bold]{'='*50}[/]"
        )
        self.app.call_from_thread(
            self._log_message,
            f"[bold]Batch Fetch Complete:[/] {success_count} success, {failure_count} failed"
        )
        self.app.call_from_thread(
            self._log_message,
            f"[dim]Output directory: {tables_dir}[/dim]"
        )

        if failed_players:
            self.app.call_from_thread(
                self._log_message, "\n[red]Failed players:[/]"
            )
            for name, error in failed_players:
                self.app.call_from_thread(
                    self._log_message, f"  • [red]{name}[/]: {error}"
                )

        # Enable back button
        self.app.call_from_thread(self._enable_back_button)

        return {
            "success": True,
            "success_count": success_count,
            "failure_count": failure_count,
            "total": len(self._players),
            "tables_dir": str(tables_dir),
            "failed_players": failed_players,
        }

    def _get_player_name(self, player: dict) -> str:
        """Get display name for a player."""
        name = player.get('name', '')
        if not name:
            firstname = player.get('firstname', player.get('firstName', ''))
            lastname = player.get('lastname', player.get('lastName', ''))
            name = f"{firstname} {lastname}".strip()
        if not name:
            name = player.get('user_id', player.get('personId', 'Unknown'))
        return name

    def _update_progress(self, completed: int, current: str) -> None:
        """Update the progress bar."""
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_bar.advance(1)
        
        status = self.query_one("#progress-status", Static)
        if current == "Complete":
            status.update(f"Complete - {completed} player(s) processed")
        else:
            status.update(f"Fetching: {current}")

    def _update_stats(self, success: int = 0, failure: int = 0, remaining: int = 0) -> None:
        """Update the statistics display."""
        success_label = self.query_one("#success-count", Static)
        failure_label = self.query_one("#failure-count", Static)
        remaining_label = self.query_one("#remaining-count", Static)
        
        success_label.update(f"✓ Success: {success}")
        failure_label.update(f"✗ Failed: {failure}")
        remaining_label.update(f"⏳ Remaining: {remaining}")

    def _log_message(self, message: str) -> None:
        """Add a message to the fetch log."""
        log = self.query_one("#fetch-log", RichLog)
        log.write(message)

    def _enable_back_button(self) -> None:
        """Enable the back button and disable cancel."""
        cancel_btn = self.query_one("#cancel-btn", Button)
        back_btn = self.query_one("#back-btn", Button)
        
        cancel_btn.disabled = True
        back_btn.disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn":
            self.action_cancel()
        elif event.button.id == "back-btn":
            self.app.pop_screen()

    def action_cancel(self) -> None:
        """Cancel the batch fetch operation."""
        self._cancelled = True
        if self._fetch_worker and self._fetch_worker.is_running:
            self._fetch_worker.cancel()
        self._log_message("[yellow]⚠ Cancelling...[/]")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes."""
        if event.worker.name != "batch_fetch_worker":
            return

        if event.state in [Worker.State.SUCCESS, Worker.State.ERROR, Worker.State.CANCELLED]:
            self._enable_back_button()
            
            if event.state == Worker.State.ERROR:
                error_msg = str(event.worker.error) if event.worker.error else "Unknown error"
                self._log_message(f"[red]❌ Worker error: {error_msg}[/]")


class UserIdInputScreen(ModalScreen[str | None]):
    """Modal screen for entering a user ID."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="userid-dialog"):
            yield Label("Enter User ID", id="userid-title")
            yield Input(placeholder="User ID (e.g., abc123...)", id="userid-input")
            with Horizontal(id="userid-buttons"):
                yield Button("Cancel", id="cancel-btn", variant="error")
                yield Button("Fetch", id="fetch-btn", variant="primary")

    def on_mount(self) -> None:
        """Focus the input on mount."""
        self.query_one("#userid-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "fetch-btn":
            user_id = self.query_one("#userid-input", Input).value.strip()
            if user_id:
                self.dismiss(user_id)
            else:
                self.notify("Please enter a user ID", severity="warning")
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel and close the modal."""
        self.dismiss(None)


class ResultScreen(ModalScreen[None]):
    """Modal screen for showing fetch results summary."""

    BINDINGS = [
        ("escape", "close", "Close"),
        ("q", "close", "Close"),
    ]

    def __init__(self, result: dict) -> None:
        super().__init__()
        self.result = result

    def compose(self) -> ComposeResult:
        with Vertical(id="result-dialog"):
            yield Label("Fetch Results", id="result-title")

            # Show summary based on result type
            if self.result.get("type") == "own_profile":
                yield Label("[green]✓ Successfully fetched your profile![/]")
            elif self.result.get("type") == "external_profile":
                user_id = self.result.get("user_id", "Unknown")
                yield Label(f"[green]✓ Successfully fetched profile for:[/] {user_id}")

            yield Label(f"\n[bold]Tables directory:[/] {self.result.get('tables_dir', 'N/A')}")

            tables = self.result.get("tables_written", [])
            if tables:
                yield Label(f"\n[bold]Files written ({len(tables)}):[/]")
                for table in tables[:10]:  # Show first 10
                    yield Label(f"  • {table}")
                if len(tables) > 10:
                    yield Label(f"  ... and {len(tables) - 10} more")
            else:
                yield Label("\n[yellow]No tables were written[/]")

            with Center():
                yield Button("Close", id="close-btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close-btn":
            self.dismiss(None)

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss(None)


class TablePreviewScreen(Screen):
    """Screen for previewing a table with filter panel and apply/reset actions.

    Features:
    - DataTable display for tabular data
    - Filter panel with column, operator, and value inputs
    - Apply action runs query in background worker and refreshes DataTable
    - Reset action clears query and shows base preview
    - Validation errors shown in status area

    Supports both in-memory Polars DataFrames and CSV files.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
        ("r", "reset", "Reset Filter"),
        ("a", "apply", "Apply Filter"),
    ]

    def __init__(
        self,
        table_name: str,
        data: Any = None,
        csv_path: str | None = None,
        limit: int = 500,
    ) -> None:
        """Initialize the table preview screen.

        Args:
            table_name: Display name for the table
            data: In-memory Polars DataFrame or PyArrow Table
            csv_path: Path to CSV file (alternative to data)
            limit: Maximum rows to display
        """
        super().__init__()
        self.table_name = table_name
        self.data = data
        self.csv_path = csv_path
        self.limit = limit
        self._query_worker: Worker | None = None
        self._columns: list[str] = []
        self._dtypes: dict[str, str] = {}
        self._base_data: Any = None  # Store original data for reset

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="table-preview-container"):
            yield Label(f"Table: {self.table_name}", id="table-preview-title")

            # Filter panel
            with Horizontal(id="filter-panel"):
                yield Label("Filter:", id="filter-label")
                yield Select(
                    options=[("Select column...", "")],
                    id="filter-column",
                    allow_blank=False,
                )
                yield Select(
                    options=[
                        ("=", "eq"),
                        ("≠", "ne"),
                        (">", "gt"),
                        ("≥", "gte"),
                        ("<", "lt"),
                        ("≤", "lte"),
                        ("contains", "contains"),
                    ],
                    id="filter-operator",
                    allow_blank=False,
                    value="eq",
                )
                yield Input(placeholder="Value", id="filter-value")
                yield Button("Apply", id="apply-btn", variant="primary")
                yield Button("Reset", id="reset-btn", variant="error")

            # Status area
            yield Static("Loading...", id="filter-status")

            # Data table
            yield DataTable(id="preview-table")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the table on mount."""
        table = self.query_one("#preview-table", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Load data in background worker
        self._query_worker = self.run_worker(
            self._load_data(),
            name="load_data_worker",
            description=f"Load table data for {self.table_name}",
        )

    async def _load_data(self) -> dict[str, Any]:
        """Background worker to load initial data.

        Returns:
            Dictionary with columns, data, and status
        """
        import polars as pl

        try:
            if self.data is not None:
                # Use in-memory data
                if hasattr(self.data, "to_polars"):
                    # PyArrow Table
                    df = self.data.to_polars()
                else:
                    # Assume Polars DataFrame
                    df = self.data
            elif self.csv_path:
                # Load from CSV
                self.app.call_from_thread(
                    self._update_status, f"[yellow]📂 Loading CSV: {self.csv_path}...[/]"
                )
                df = pl.read_csv(self.csv_path)
            else:
                return {"success": False, "error": "No data source provided"}

            # Store base data for reset
            self._base_data = df.clone()

            # Get column info
            columns = df.columns
            dtypes = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}

            # Apply initial limit
            if self.limit:
                df = df.head(self.limit)

            return {
                "success": True,
                "columns": columns,
                "dtypes": dtypes,
                "df": df,
                "row_count": len(self._base_data),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _update_status(self, message: str) -> None:
        """Update the status display.

        Args:
            message: Status message to display
        """
        status = self.query_one("#filter-status", Static)
        status.update(message)

    def _update_column_select(self, columns: list[str], dtypes: dict[str, str]) -> None:
        """Update the column dropdown with available columns.

        Args:
            columns: List of column names
            dtypes: Dictionary mapping column names to types
        """
        self._columns = columns
        self._dtypes = dtypes

        column_select = self.query_one("#filter-column", Select)
        options = [(f"{col} ({dtypes.get(col, 'unknown')})", col) for col in columns]
        column_select.set_options(options)
        if options:
            column_select.value = options[0][1]

    def _populate_table(self, df: Any) -> None:
        """Populate the DataTable with data.

        Args:
            df: Polars DataFrame
        """
        import polars as pl

        table = self.query_one("#preview-table", DataTable)
        table.clear(columns=True)

        # Add columns
        columns = df.columns
        table.add_columns(*columns)

        # Add rows (convert to list of lists for DataTable)
        rows = df.rows()
        for row in rows:
            # Convert each value to string for display
            str_row = [str(v) if v is not None else "" for v in row]
            table.add_row(*str_row)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes.

        Args:
            event: Worker state change event
        """
        if event.worker.name == "load_data_worker":
            if event.state == Worker.State.SUCCESS:
                result = event.worker.result
                if result and result.get("success"):
                    self._update_column_select(result["columns"], result["dtypes"])
                    self._populate_table(result["df"])
                    row_count = result.get("row_count", 0)
                    self._update_status(
                        f"[green]✓ Loaded {row_count} rows[/]"
                    )
                else:
                    error = result.get("error", "Unknown error") if result else "Unknown error"
                    self._update_status(f"[red]❌ Error: {error}[/]")
            elif event.state == Worker.State.ERROR:
                error_msg = str(event.worker.error) if event.worker.error else "Unknown error"
                self._update_status(f"[red]❌ Error: {error_msg}[/]")

        elif event.worker.name == "filter_worker":
            if event.state == Worker.State.SUCCESS:
                result = event.worker.result
                if result and result.get("success"):
                    self._populate_table(result["df"])
                    filtered_count = result.get("filtered_count", 0)
                    total_count = result.get("total_count", 0)
                    self._update_status(
                        f"[green]✓ Showing {filtered_count} of {total_count} rows[/]"
                    )
                else:
                    error = result.get("error", "Unknown error") if result else "Unknown error"
                    self._update_status(f"[red]❌ Filter error: {error}[/]")
            elif event.state == Worker.State.ERROR:
                error_msg = str(event.worker.error) if event.worker.error else "Unknown error"
                self._update_status(f"[red]❌ Filter error: {error_msg}[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button press event
        """
        if event.button.id == "apply-btn":
            self._apply_filter()
        elif event.button.id == "reset-btn":
            self._reset_filter()

    def _get_filter_from_ui(self) -> Filter | None:
        """Build a Filter from the UI inputs.

        Returns:
            Filter object or None if invalid
        """
        column_select = self.query_one("#filter-column", Select)
        operator_select = self.query_one("#filter-operator", Select)
        value_input = self.query_one("#filter-value", Input)

        column = column_select.value
        if not column:
            return None

        op_str = operator_select.value or "eq"
        op_map = {
            "eq": FilterOp.EQ,
            "ne": FilterOp.NE,
            "gt": FilterOp.GT,
            "gte": FilterOp.GTE,
            "lt": FilterOp.LT,
            "lte": FilterOp.LTE,
            "contains": FilterOp.CONTAINS,
        }
        op = op_map.get(op_str, FilterOp.EQ)

        value = value_input.value.strip()
        if not value and op not in (FilterOp.IS_NULL, FilterOp.IS_NOT_NULL):
            return None

        # Try to convert value based on column type
        dtype = self._dtypes.get(column, "").lower()
        if "int" in dtype:
            try:
                value = int(value)
            except ValueError:
                self._update_status(f"[red]❌ Invalid integer: {value}[/]")
                return None
        elif "float" in dtype or "double" in dtype:
            try:
                value = float(value)
            except ValueError:
                self._update_status(f"[red]❌ Invalid number: {value}[/]")
                return None

        return Filter(column, op, value)

    def _apply_filter(self) -> None:
        """Apply the filter and refresh the table."""
        filter_spec = self._get_filter_from_ui()
        if not filter_spec:
            self._update_status("[red]❌ Please select a column and enter a value[/]")
            return

        # Disable apply button during query
        apply_btn = self.query_one("#apply-btn", Button)
        apply_btn.disabled = True
        apply_btn.label = "Applying..."

        self._update_status("[yellow]🔄 Applying filter...[/]")

        # Run filter in background worker
        self._query_worker = self.run_worker(
            self._do_filter(filter_spec),
            name="filter_worker",
            description="Apply filter to table",
        )

    async def _do_filter(self, filter_spec: Filter) -> dict[str, Any]:
        """Background worker to apply filter.

        Args:
            filter_spec: Filter specification

        Returns:
            Dictionary with filtered data and status
        """
        import polars as pl

        try:
            if self._base_data is None:
                return {"success": False, "error": "No data loaded"}

            # Build query with filter
            query = Query(
                filters=[filter_spec],
                limit=self.limit,
            )

            # Execute query
            executor = PolarsQueryExecutor(validate=True)
            result_df = executor.execute(self._base_data, query)

            return {
                "success": True,
                "df": result_df,
                "filtered_count": len(result_df),
                "total_count": len(self._base_data),
            }

        except ValidationError as e:
            return {"success": False, "error": str(e)}
        except QueryExecutorError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {e}"}

    def _reset_filter(self) -> None:
        """Reset the filter and show base preview."""
        import polars as pl

        # Clear filter inputs
        value_input = self.query_one("#filter-value", Input)
        value_input.value = ""

        # Reset to base data
        if self._base_data is not None:
            df = self._base_data.head(self.limit) if self.limit else self._base_data
            self._populate_table(df)
            total_count = len(self._base_data)
            self._update_status(f"[green]✓ Reset - showing {min(self.limit or total_count, total_count)} of {total_count} rows[/]")

    def action_back(self) -> None:
        """Return to previous screen."""
        # Cancel any running worker
        if self._query_worker and self._query_worker.is_running:
            self._query_worker.cancel()
        self.app.pop_screen()

    def action_reset(self) -> None:
        """Reset filter action (key binding)."""
        self._reset_filter()

    def action_apply(self) -> None:
        """Apply filter action (key binding)."""
        self._apply_filter()
