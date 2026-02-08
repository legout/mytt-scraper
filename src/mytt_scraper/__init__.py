"""MyTischtennis.de Scraper

A Python package for logging into mytischtennis.de and fetching player data
including TTR rankings, league tables, and match history.
"""

from .config import (
    API_HEADERS,
    BASE_URL,
    EXTERNAL_PROFILE_ENDPOINT,
    LOGIN_URL,
    OWN_PROFILE_ENDPOINT,
    TABLES_DIR_NAME,
)
from .player_search import PlayerSearcher
from .scraper import MyTischtennisScraper

# In-memory table extraction - available both as module-level function
# and as method on MyTischtennisScraper instance
from .utils import extract_flat_tables

__all__ = [
    "MyTischtennisScraper",
    "PlayerSearcher",
    "BASE_URL",
    "LOGIN_URL",
    "OWN_PROFILE_ENDPOINT",
    "EXTERNAL_PROFILE_ENDPOINT",
    "API_HEADERS",
    "TABLES_DIR_NAME",
    "extract_flat_tables",
]

__version__ = "0.1.0"
