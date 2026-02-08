"""TUI Screens for mytt-scraper."""

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

__all__ = ["LoginScreen", "MainMenuScreen", "SearchScreen"]


class LoginScreen(Screen):
    """Screen for user login with username/password."""

    BINDINGS = [("q", "quit", "Quit")]

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
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            status = self.query_one("#login-status", Static)

            if not username or not password:
                status.update("[red]Please enter both username and password[/]")
                return

            # Placeholder: In full implementation, this would run Playwright login
            # WARNING: This is a placeholder - no actual authentication is performed
            status.update(
                "[yellow]⚠️  AUTH NOT IMPLEMENTED - Skipping to main menu[/]"
            )
            # Transition to main menu (placeholder behavior)
            self.app.push_screen("main_menu")


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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle menu button presses."""
        button_id = event.button.id

        if button_id == "fetch-profile":
            self.notify("Fetch profile - not yet implemented", severity="warning")
        elif button_id == "search-players":
            self.app.push_screen("search")
        elif button_id == "fetch-by-id":
            self.notify("Fetch by ID - not yet implemented", severity="warning")

    def action_logout(self) -> None:
        """Return to login screen."""
        self.app.pop_screen()


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
