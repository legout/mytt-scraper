"""Main Textual App for mytt-scraper TUI."""

from pathlib import Path
from typing import Any, Optional

from textual.app import App
from textual.reactive import reactive
from textual.widgets import Footer, Header

from ..scraper import MyTischtennisScraper
from ..player_search import PlayerSearcher
from ..utils.table_provider import TableProvider, TableInfo, TableSource, create_default_provider
from .screens import LoginScreen, MainMenuScreen, SearchScreen, UserIdInputScreen, ResultScreen, BatchFetchScreen, TablePreviewScreen, TableListScreen

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
    
    # Reactive state for in-memory tables from fetch operations
    # Dictionary mapping table names to DataFrame/Table objects
    tables: reactive[dict[str, Any]] = reactive({})

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

    /* Selection Controls */
    #selection-controls {
        height: auto;
        margin: 1 0;
        align: center middle;
    }

    #selection-controls Button {
        width: auto;
        margin: 0 1;
    }

    #selection-count {
        width: auto;
        margin-left: 2;
        content-align: center middle;
    }

    /* Batch Fetch Screen Styles */
    #batch-fetch-container {
        align: center middle;
        width: 100;
        height: 95%;
        border: solid green;
        padding: 1 2;
    }

    #batch-fetch-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    /* Table Preview Screen Styles */
    #table-preview-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #table-preview-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    /* Table List Screen Styles */
    #source-legend {
        height: auto;
        margin: 1 0;
        align: center middle;
    }

    #source-legend-text {
        color: $text-muted;
        text-align: center;
    }

    #filter-panel {
        height: auto;
        margin: 1 0;
        align: left middle;
    }

    #filter-panel Label {
        width: auto;
        margin-right: 1;
    }

    #filter-column {
        width: 30;
        margin-right: 1;
    }

    #filter-operator {
        width: 15;
        margin-right: 1;
    }

    #filter-value {
        width: 25;
        margin-right: 1;
    }

    #apply-btn, #reset-btn {
        width: auto;
        margin: 0 1;
    }

    #filter-status {
        height: auto;
        margin: 1 0;
        text-align: center;
    }

    #preview-table {
        height: 1fr;
        border: solid $primary;
    }

    #preview-table:focus {
        border: solid $accent;
    }

    /* SQL Query Mode Styles */
    #query-mode-toggle {
        height: auto;
        margin: 1 0;
        align: left middle;
    }

    #query-mode-toggle Label {
        width: auto;
        margin-right: 1;
    }

    #mode-label {
        width: auto;
        margin-left: 1;
        color: $text-muted;
    }

    #sql-input-container {
        height: auto;
        margin: 1 0;
    }

    #sql-input {
        height: 6;
        border: solid $primary;
    }

    #sql-actions {
        height: auto;
        margin: 1 0;
        align: center middle;
    }

    #progress-section {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid $primary-darken-2;
    }

    #progress-status {
        text-align: center;
        margin-bottom: 1;
    }

    #stats-section {
        height: auto;
        margin: 1 0;
        align: center middle;
    }

    #stats-section .stat {
        width: 1fr;
        text-align: center;
        padding: 0 1;
    }

    #log-label {
        margin-top: 1;
        text-style: bold;
    }

    #fetch-log {
        height: 1fr;
        border: solid $primary;
        padding: 1;
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
        "table_preview": TablePreviewScreen,
        "table_list": TableListScreen,
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
    
    def set_tables(self, tables: dict[str, Any]) -> None:
        """Store in-memory tables from a fetch operation.
        
        These tables are available session-wide for viewing.
        
        Args:
            tables: Dictionary mapping table names to DataFrame/Table objects
        """
        self.tables = tables
    
    def get_tables(self) -> dict[str, Any]:
        """Get the current in-memory tables.
        
        Returns:
            Dictionary of table name -> DataFrame/Table, or empty dict if none
        """
        return self.tables
    
    def clear_tables(self) -> None:
        """Clear all stored in-memory tables."""
        self.tables = {}
    
    def has_tables(self) -> bool:
        """Check if any in-memory tables are available.
        
        Returns:
            True if tables exist, False otherwise
        """
        return len(self.tables) > 0
    
    def get_table_provider(self, tables_dir: str | Path = "tables") -> TableProvider:
        """Get a TableProvider for discovering and accessing tables.
        
        Provides unified access to both in-memory (current session) and
        disk-based (CSV files) tables with friendly display names.
        
        Args:
            tables_dir: Path to the tables directory for disk-based tables
            
        Returns:
            Configured TableProvider instance
        """
        provider = create_default_provider(
            memory_tables=self.tables,
            tables_dir=tables_dir,
        )
        return provider
    
    def discover_tables(self, include_disk: bool = True) -> list[TableInfo]:
        """Discover all available tables from memory and disk.
        
        Args:
            include_disk: Whether to include disk-based tables (default: True)
            
        Returns:
            List of TableInfo objects with metadata for each table
        """
        provider = self.get_table_provider()
        return provider.discover(include_disk=include_disk)
    
    def has_any_tables(self, include_disk: bool = True) -> bool:
        """Check if any tables are available from any source.
        
        Args:
            include_disk: Whether to check disk-based tables (default: True)
            
        Returns:
            True if tables exist in memory or on disk
        """
        if self.has_tables():
            return True
        if include_disk:
            provider = self.get_table_provider()
            disk_tables = provider.discover(include_disk=True)
            return any(t.source == TableSource.DISK for t in disk_tables)
        return False
