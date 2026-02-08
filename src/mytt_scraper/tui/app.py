"""Main Textual App for mytt-scraper TUI."""

from typing import Optional

from textual.app import App
from textual.reactive import reactive
from textual.widgets import Footer, Header

from ..scraper import MyTischtennisScraper
from ..player_search import PlayerSearcher
from .screens import LoginScreen, MainMenuScreen, SearchScreen, UserIdInputScreen, ResultScreen

__all__ = ["MyttScraperApp"]


class MyttScraperApp(App):
    """Textual TUI application for mytischtennis.de scraper.
    
    Provides screens for:
    - Login (username/password)
    - Main menu (fetch profile, search, fetch by ID)
    - Search (find players by name)
    
    App state:
    - scraper: Authenticated MyTischtennisScraper instance (session-only)
    """
    
    # Reactive state for authenticated scraper instance
    scraper: reactive[Optional[MyTischtennisScraper]] = reactive(None)

    CSS = """
    #login-container, #menu-container, #search-container {
        align: center middle;
        width: 80;
        height: auto;
        border: solid green;
        padding: 1 2;
    }

    #search-container {
        width: 100;
        height: 90%;
    }

    #login-title, #menu-title, #search-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #login-status, #search-status, #menu-status {
        margin-top: 1;
        margin-bottom: 1;
        text-align: center;
    }

    #userid-dialog, #result-dialog {
        align: center middle;
        width: 60;
        height: auto;
        border: solid blue;
        padding: 1 2;
        background: $surface;
    }

    /* Search Screen Styles */
    #search-options {
        height: auto;
        margin: 1 0;
        align: left middle;
    }

    #search-options Label {
        width: auto;
        margin-right: 1;
    }

    #search-options Switch {
        margin-right: 1;
    }

    #mode-indicator {
        width: auto;
        color: $text-muted;
    }

    #results-table {
        height: 1fr;
        margin: 1 0;
        border: solid $primary;
    }

    #results-table:focus {
        border: solid $accent;
    }

    #selection-bar {
        height: auto;
        margin-top: 1;
        align: left middle;
    }

    #selection-info {
        width: 1fr;
        content-align: left middle;
    }

    #userid-title, #result-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #userid-buttons {
        align: center middle;
        margin-top: 1;
    }

    #userid-buttons Button {
        margin: 0 1;
    }

    Button {
        width: 30;
        margin: 1;
    }

    Input {
        margin: 1 0;
    }

    Screen {
        align: center middle;
    }
    """

    SCREENS = {
        "login": LoginScreen,
        "main_menu": MainMenuScreen,
        "search": SearchScreen,
        "user_id_input": UserIdInputScreen,
        "result": ResultScreen,
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+d", "toggle_dark", "Toggle Dark"),
    ]

    def on_mount(self) -> None:
        """Initialize the app on mount."""
        self.title = "MyTischtennis Scraper"
        self.push_screen("login")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark
    
    def set_scraper(self, username: str, password: str, headless: bool = True) -> MyTischtennisScraper:
        """Create and store an authenticated scraper instance.
        
        Args:
            username: Email/username for login
            password: Password for login
            headless: Whether to run browser in headless mode
            
        Returns:
            Configured MyTischtennisScraper instance
        """
        self.scraper = MyTischtennisScraper(username, password, headless=headless)
        return self.scraper
    
    def set_searcher(self, username: str, password: str, headless: bool = True) -> PlayerSearcher:
        """Create and store an authenticated PlayerSearcher instance.
        
        Args:
            username: Email/username for login
            password: Password for login
            headless: Whether to run browser in headless mode
            
        Returns:
            Configured PlayerSearcher instance
        """
        self.scraper = PlayerSearcher(username, password, headless=headless)
        return self.scraper
    
    def clear_scraper(self) -> None:
        """Clear the stored scraper instance (logout)."""
        self.scraper = None
    
    def get_scraper(self) -> Optional[MyTischtennisScraper]:
        """Get the current authenticated scraper instance.
        
        Returns:
            The stored scraper instance, or None if not authenticated
        """
        return self.scraper
    
    def is_authenticated(self) -> bool:
        """Check if a scraper instance is stored.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self.scraper is not None
