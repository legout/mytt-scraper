"""TUI Screens for mytt-scraper."""

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static
from textual.worker import Worker

from ..utils.auth import login_with_playwright

__all__ = ["LoginScreen", "MainMenuScreen", "SearchScreen"]


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
    """Main menu screen with navigation to all features."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("l", "logout", "Logout"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="menu-container"):
            yield Label("Main Menu", id="menu-title")
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu button presses."""
        button_id = event.button.id

        if button_id == "fetch-profile":
            scraper = self.app.get_scraper()
            if scraper:
                self.notify("Fetching your profile...", severity="information")
                # TODO: Run fetch in background worker
            else:
                self.notify("Not authenticated", severity="error")
        elif button_id == "search-players":
            self.app.push_screen("search")
        elif button_id == "fetch-by-id":
            self.notify("Fetch by ID - not yet implemented", severity="warning")

    def action_logout(self) -> None:
        """Logout and return to login screen."""
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
