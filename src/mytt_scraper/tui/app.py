"""Main Textual App for mytt-scraper TUI."""

from textual.app import App
from textual.widgets import Footer, Header

from .screens import LoginScreen, MainMenuScreen, SearchScreen

__all__ = ["MyttScraperApp"]


class MyttScraperApp(App):
    """Textual TUI application for mytischtennis.de scraper.
    
    Provides screens for:
    - Login (username/password)
    - Main menu (fetch profile, search, fetch by ID)
    - Search (find players by name)
    """

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
