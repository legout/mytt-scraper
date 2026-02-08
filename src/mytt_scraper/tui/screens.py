"""TUI Screens for mytt-scraper."""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Center, Vertical, Horizontal
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, Static, DataTable
from textual.worker import Worker

from ..utils.auth import login_with_playwright

__all__ = ["LoginScreen", "MainMenuScreen", "SearchScreen", "UserIdInputScreen", "ResultScreen"]


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
    """Screen for searching players."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="search-container"):
            yield Label("Search Players", id="search-title")
            yield Input(placeholder="Search by name...", id="search-input")
            with Center():
                yield Button("Search", id="search-btn", variant="primary")
            yield Static("Enter a name to search", id="search-status")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle search button press."""
        if event.button.id == "search-btn":
            query = self.query_one("#search-input", Input).value
            status = self.query_one("#search-status", Static)

            if not query:
                status.update("[red]Please enter a search term[/]")
                return

            # Placeholder: In full implementation, this would call search_players
            status.update(f"[yellow]Searching for '{query}'... (placeholder)[/]")

    def action_back(self) -> None:
        """Return to main menu."""
        self.app.pop_screen()


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
