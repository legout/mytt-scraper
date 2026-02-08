"""Main scraper class for mytt_scraper"""

import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Literal, Optional
from datetime import datetime

import requests

from .config import (
    BASE_URL,
    OWN_PROFILE_ENDPOINT,
    EXTERNAL_PROFILE_ENDPOINT,
    API_HEADERS,
    TABLES_DIR_NAME,
)
from .utils import parse_multipart_json, extract_flat_tables as _extract_flat_tables
from .utils.table_extractor import (
    extract_club_info_table,
    extract_ttr_rankings_table,
    extract_league_table,
    extract_ttr_history_events_table,
    extract_ttr_history_matches_table,
)
from .utils.auth import login

# Supported backend types for in-memory table extraction
Backend = Literal["polars", "pandas", "pyarrow"]


class MyTischtennisScraper:
    """Main scraper class for fetching data from mytischtennis.de"""

    def __init__(self, username: str, password: str, headless: bool = True, tables_dir: Optional[Path] = None):
        """
        Initialize the scraper.

        Args:
            username: Email/username for login
            password: Password for login
            headless: Whether to run browser in headless mode
            tables_dir: Custom directory for tables (defaults to 'tables')
        """
        self.username = username
        self.password = password
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.headless = headless
        self.tables_dir = tables_dir or Path(TABLES_DIR_NAME)
        self.tables_dir.mkdir(exist_ok=True)

    def login(self) -> bool:
        """Login to mytischtennis.de"""
        return login(self.username, self.password, self.headless, self.session.cookies)

    def fetch_data(self, url: str, description: str):
        """
        Fetch data from a given URL.

        Args:
            url: URL to fetch from
            description: Description of what is being fetched

        Returns:
            Tuple of (parsed_data, remaining_text)
        """
        print(f"\nFetching: {description}")
        print(f"URL: {url}")

        try:
            # Update headers for the fetch request
            self.session.headers.update(API_HEADERS)

            response = self.session.get(url)
            print(f"Response status: {response.status_code}")

            if response.status_code == 200:
                print(f"Content-Type: {response.headers.get('Content-Type')}")

                # Parse the multipart JSON response
                data, remaining = parse_multipart_json(response.text)
                print(f"✓ Successfully fetched and parsed data")

                return data, remaining
            else:
                print(f"✗ Request failed with status {response.status_code}")
                print("Response:", response.text[:500])
                return None, None

        except requests.RequestException as e:
            print(f"✗ Error fetching data: {e}")
            return None, None

    def fetch_own_community(self):
        """Fetch own community/profile data"""
        url = OWN_PROFILE_ENDPOINT
        return self.fetch_data(url, "Own community data")

    def fetch_external_profile(self, user_id: str):
        """
        Fetch external profile data for a specific user.

        Args:
            user_id: User ID to fetch profile for
        """
        url = EXTERNAL_PROFILE_ENDPOINT.format(user_id=user_id)
        return self.fetch_data(url, f"External profile (user-id: {user_id})")

    def extract_and_save_tables(self, data: Dict[str, Any], remaining: str = None, prefix: str = '') -> None:
        """
        Extract all flat tables from the response data.

        Args:
            data: Main response data
            remaining: Remaining text containing deferred data
            prefix: Optional filename prefix
        """
        if not data:
            print("No data to extract tables from")
            return

        print(f"\n{'='*60}")
        print(f"Extracting tables{' (prefix: ' + prefix + ')' if prefix else ''}")
        print(f"{'='*60}\n")

        # 1. Club Info
        if 'pageContent' in data and 'blockLoaderData' in data['pageContent']:
            block_loader = data['pageContent']['blockLoaderData']

            # Find block with club info
            for block_id, block_data in block_loader.items():
                if isinstance(block_data, dict):
                    # Club info
                    if any(field in block_data for field in ['clubNr', 'association', 'season', 'group_name']):
                        extract_club_info_table(block_data, self.tables_dir, prefix)

                    # TTR Rankings
                    if 'clubTtrRanking' in block_data:
                        extract_ttr_rankings_table(block_data, self.tables_dir, prefix)

                    # League Table
                    if 'teamLeagueRanking' in block_data:
                        extract_league_table(block_data, self.tables_dir, prefix)

        # 2. TTR History (from remaining data)
        if remaining:
            self._extract_ttr_history(remaining, prefix)

        print(f"\n{'='*60}")
        print(f"✓ All tables extracted")
        print(f"{'='*60}")

    def extract_flat_tables(self, data: Dict[str, Any], remaining: str = None, backend: Backend = "polars") -> Dict[str, Any]:
        """
        Extract flat tables from fetched profile data as in-memory objects.

        This is a convenience wrapper around the module-level `extract_flat_tables()`
        function, allowing callers to extract tables without importing from utils.

        Args:
            data: Main response data from fetch_own_community() or fetch_external_profile()
            remaining: Optional remaining text containing deferred TTR history data
            backend: Output format - "polars", "pandas", or "pyarrow"

        Returns:
            Dictionary mapping table names to DataFrame/Table objects.
            Missing tables are omitted from the result.

            Table names: club_info, ttr_rankings, league_table,
                        ttr_history_events, ttr_history_matches

        Raises:
            ValueError: If an unsupported backend is specified

        Example:
            >>> scraper = MyTischtennisScraper(username, password)
            >>> scraper.login()
            >>> data, remaining = scraper.fetch_own_community()
            >>> tables = scraper.extract_flat_tables(data, remaining, backend="polars")
            >>> print(tables["ttr_rankings"].head())
        """
        return _extract_flat_tables(data, remaining, backend=backend)

    def _extract_ttr_history(self, remaining: str, prefix: str = '') -> None:
        """
        Extract TTR history from remaining data.

        Args:
            remaining: Remaining text containing deferred data
            prefix: Optional filename prefix
        """
        # The deferred data is in format: data:{"key|data":{"ttr":...,"event":[...]}}
        if 'data:' not in remaining:
            print("No 'data:' prefix found in response")
            return

        try:
            # Find data: and extract everything after it
            data_start = remaining.find('data:') + 5
            data_str = remaining[data_start:].strip()

            # Try to parse the JSON
            parsed = json.loads(data_str)

            # Look for a key that contains ttr and event data
            for key, value in parsed.items():
                if isinstance(value, dict) and 'ttr' in value and 'event' in value:
                    history = value
                    extract_ttr_history_events_table(history, self.tables_dir, prefix)
                    extract_ttr_history_matches_table(history, self.tables_dir, prefix)
                    print(f"✓ Found TTR history with {len(history['event'])} events")
                    return
        except json.JSONDecodeError as e:
            print(f"Could not parse TTR history data as JSON: {e}")

            # Try alternative approach: find the nested JSON object
            try:
                nested_match = re.search(r'".*\|data":(\{.*\})\}', remaining)
                if nested_match:
                    nested_json = nested_match.group(1)
                    history = json.loads(nested_json)
                    if 'ttr' in history and 'event' in history:
                        extract_ttr_history_events_table(history, self.tables_dir, prefix)
                        extract_ttr_history_matches_table(history, self.tables_dir, prefix)
                        print(f"✓ Found TTR history with {len(history['event'])} events (alternative parsing)")
                        return
            except Exception as e2:
                print(f"Alternative parsing also failed: {e2}")
        except Exception as e:
            print(f"Error parsing TTR history: {e}")

        print("No TTR history data found in response")

    def run_own_profile(self) -> Optional[Dict[str, Any]]:
        """
        Run the complete workflow for own profile.

        Returns:
            Profile data if successful, None otherwise
        """
        # Login
        if self.login():
            # Fetch own community data
            data, remaining = self.fetch_own_community()

            if data:
                # Extract and save tables
                self.extract_and_save_tables(data, remaining)
                return data

        return None

    def run_external_profile(self, user_id: str, prefix: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Run the workflow for an external profile.

        Args:
            user_id: User ID to fetch
            prefix: Optional filename prefix

        Returns:
            Profile data if successful, None otherwise
        """
        # Ensure we're logged in
        if not self.session.cookies:
            print("Not logged in. Please login first.")
            return None

        # Use user_id as prefix if not provided
        if prefix is None:
            prefix = f"{user_id}_"

        # Fetch external profile data
        data, remaining = self.fetch_external_profile(user_id)

        if data:
            # Extract and save tables with prefix
            self.extract_and_save_tables(data, remaining, prefix)
            return data

        return None

    def run_multiple_profiles(self, user_ids: List[str]) -> Dict[str, Any]:
        """
        Fetch data for multiple profiles.

        Args:
            user_ids: List of user IDs to fetch

        Returns:
            Dictionary mapping user IDs to their data
        """
        results = {}

        for i, user_id in enumerate(user_ids, 1):
            print(f"\n{'='*60}")
            print(f"Processing profile {i}/{len(user_ids)}: {user_id}")
            print(f"{'='*60}")

            data = self.run_external_profile(user_id)
            results[user_id] = data

            # Small delay between requests
            if i < len(user_ids):
                time.sleep(1)

        return results
