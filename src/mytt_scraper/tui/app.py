"""Main Textual App for mytt-scraper TUI."""

from typing import Optional

from textual.app import App
from textual.reactive import reactive
from textual.widgets import Footer, Header

from ..scraper import MyTischtennisScraper
from ..player_search import PlayerSearcher
from .screens import LoginScreen, MainMenuScreen, SearchScreen

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
        width: 60;
        height: auto;
        border: solid green;
        padding: 1 2;
    }
    
    #login-title, #menu-title, #search-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #login-status, #search-status {
        margin-top: 1;
        text-align: center;
    }
    
    Button {
        width: 30;
        margin: 1;
    }
    
    Input {
        margin: 1 0;
    }
    """

    SCREENS = {
        "login": LoginScreen,
        "main_menu": MainMenuScreen,
        "search": SearchScreen,
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
