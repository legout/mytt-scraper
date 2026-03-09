"""Player search functionality for mytt_scraper"""

import asyncio
import time
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests
from playwright.async_api import async_playwright

from .scraper import MyTischtennisScraper
from .config import BASE_URL, COMMUNITY_URL, SEARCH_INPUT_SELECTORS, SEARCH_RESULTS_FIELDS


class PlayerSearcher(MyTischtennisScraper):
    """Extends MyTischtennisScraper with player search functionality"""

    def search_players(self, query: str, use_playwright: bool = False) -> List[Dict[str, Any]]:
        """
        Search for players on mytischtennis.de.

        Args:
            query: Search term (player name, club, etc.)
            use_playwright: If True, use browser to interact with search UI

        Returns:
            List of player dictionaries with user-id
        """
        print(f"\nSearching for players: '{query}'")

        if not use_playwright:
            # Try API endpoints first
            results = self._search_via_api(query)
            if results:
                return results

        # Fallback to Playwright search
        return asyncio.run(self._search_via_playwright(query))

    def _search_via_api(self, query: str) -> List[Dict[str, Any]]:
        """Search for players using the mytischtennis.de search API.
        
        The actual search endpoint is:
        POST https://www.mytischtennis.de/api/search/players
        Body: query={search_term}&page=1&pagesize=4
        
        Returns player data with fields:
        - lastname, firstname
        - person_id
        - external_id (this is the user-id for fetching profiles)
        - internal_id
        - licence_club
        - club_name
        """
        search_url = f"{BASE_URL}/api/search/players"
        
        print(f"Searching API: {search_url}")
        print(f"  Query: '{query}'")
        
        try:
            # The API expects form-encoded data
            data = {
                'query': query,
                'page': '1',
                'pagesize': '20'  # Get more results
            }
            
            response = self.session.post(search_url, data=data)
            print(f"  Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    if 'results' in result and isinstance(result['results'], list):
                        players = []
                        for item in result['results']:
                            player = self._parse_search_api_player(item)
                            if player:
                                players.append(player)
                        
                        print(f"✓ Found {len(players)} player(s) via search API")
                        return players
                    else:
                        print(f"  No 'results' in response. Keys: {list(result.keys())}")
                        
                except Exception as e:
                    print(f"  JSON parse error: {e}")
                    print(f"  Response text: {response.text[:500]}")
            else:
                print(f"  Request failed: {response.status_code}")
                print(f"  Response: {response.text[:500]}")
                
        except requests.RequestException as e:
            print(f"  Request error: {e}")

        return []
    
    def _parse_search_api_player(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a player item from the search API response.
        
        The search API returns:
        {
            "lastname": "Müller-Dietrich",
            "firstname": "Birte",
            "person_id": 314315,
            "external_id": "e23825d6-d6b8-4186-b217-96b88e0a5d85",
            "internal_id": "NU37332",
            "licence_club": "SG 1947 Freiensteinau (24015)",
            "dttb_player_id": null,
            "club_name": "SG 1947 Freiensteinau"
        }
        """
        if not isinstance(item, dict):
            return None
        
        # Map the API fields to our standard format
        player = {
            'user_id': item.get('external_id'),  # This is the key for fetching profiles
            'personId': str(item.get('person_id', '')),
            'external_id': item.get('external_id'),
            'internal_id': item.get('internal_id'),
            'name': f"{item.get('firstname', '')} {item.get('lastname', '')}".strip(),
            'firstname': item.get('firstname'),
            'lastname': item.get('lastname'),
            'club': item.get('club_name') or item.get('licence_club'),
            'clubNr': None,  # Will be extracted from licence_club if needed
            'ttr': None,  # Search API doesn't return TTR
            'source': 'search_api'
        }
        
        # Only return if we have the essential user_id
        if player['user_id']:
            return player
        
        return None

    def _extract_players_from_block_loader(self, block_loader: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract players from blockLoaderData structure."""
        players = []
        
        for block_id, block_data in block_loader.items():
            if not isinstance(block_data, dict):
                continue
                
            # Look for various player list keys
            player_keys = ['players', 'searchResults', 'results', 'opponents', 'members', 'items']
            
            for key in player_keys:
                if key in block_data and isinstance(block_data[key], list):
                    for item in block_data[key]:
                        player = self._parse_player_item(item)
                        if player:
                            players.append(player)
        
        return players

    def _extract_players_from_page(self, page_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract player info from pageContent structure"""
        players = []

        # Check blockLoaderData
        if 'blockLoaderData' in page_content:
            for block_id, block_data in page_content['blockLoaderData'].items():
                if isinstance(block_data, dict):
                    # Look for player blocks
                    for key in ['opponents', 'players', 'clubTtrRanking']:
                        if key in block_data and isinstance(block_data[key], list):
                            for item in block_data[key]:
                                player = self._parse_player_item(item)
                                if player:
                                    players.append(player)

        # Check blocks
        if 'blocks' in page_content:
            for block in page_content['blocks']:
                if isinstance(block, dict) and 'content' in block:
                    content = block['content']
                    for key in ['opponents', 'players', 'members']:
                        if key in content and isinstance(content[key], list):
                            for item in content[key]:
                                player = self._parse_player_item(item)
                                if player:
                                    players.append(player)

        return players

    def _parse_player_item(self, item: Any) -> Optional[Dict[str, Any]]:
        """Parse a single player item"""
        if not isinstance(item, dict):
            return None

        player = {}

        # Common field mappings
        field_map = {
            'user_id': ['userId', 'user-id', 'id', 'personId', 'person_id'],
            'name': ['name', 'fullname', 'displayName'],
            'firstname': ['firstname', 'firstName', 'vorname'],
            'lastname': ['lastname', 'lastName', 'nachname'],
            'club': ['clubName', 'club', 'verein'],
            'clubNr': ['clubNr', 'club_nr'],
            'ttr': ['ttr', 'rank', 'ranking'],
            'external_id': ['external_id', 'externalId'],
            'personId': ['personId', 'person_id'],
        }

        for target_field, source_fields in field_map.items():
            for source_field in source_fields:
                if source_field in item and item[source_field]:
                    player[target_field] = item[source_field]
                    break

        # Return if we found at least some identifying info
        if 'name' in player or 'personId' in player or 'user_id' in player:
            return player

        return None

    def _extract_players_from_html(self, html: str) -> List[Dict[str, Any]]:
        """Extract player information from HTML"""
        players = []

        # Look for external-profile links
        pattern = r'/community/external-profile\?user-id=([a-f0-9-]+)'
        matches = re.findall(pattern, html)

        for match in set(matches):  # Use set to deduplicate
            user_id = match
            player = {'user_id': user_id, 'source': 'html'}
            players.append(player)

        return players

    async def _search_via_playwright(self, query: str) -> List[Dict[str, Any]]:
        """Use Playwright to search via the API.
        
        Since we now know the correct API endpoint, we use Playwright
        to ensure we have a valid authenticated session, then call the API.
        """
        print("Using Playwright for search...")
        
        # Actually, since we now have the correct API endpoint,
        # we'll just use the API method which is faster and more reliable.
        # But we'll do a quick browser check to ensure session is valid.
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='de-DE',
            )

            # Transfer cookies from our session to browser
            cookies = [{'name': c.name, 'value': c.value, 'domain': '.mytischtennis.de'} for c in self.session.cookies]
            await context.add_cookies(cookies)

            page = await context.new_page()

            try:
                # Navigate to community page to verify session is valid
                print(f"Verifying session...")
                await page.goto(f"{BASE_URL}/community", wait_until='domcontentloaded')
                await asyncio.sleep(2)
                
                # If we're redirected to login, session expired
                if '/login' in page.url:
                    print("⚠ Session expired, need to re-login")
                    await browser.close()
                    return []
                
                print("✓ Session is valid")
                await browser.close()
                
                # Now use the API method which is more reliable
                return self._search_via_api(query)

            except Exception as e:
                print(f"Error during Playwright session check: {e}")
                await browser.close()
                # Fall back to API method anyway
                return self._search_via_api(query)

    def _display_search_results(self, results: List[Dict[str, Any]], query: str) -> None:
        """Display search results"""
        print(f"\n{'='*60}")
        print(f" Search Results for '{query}'")
        print(f"{'='*60}")

        if not results:
            print("No results found")
            return

        print(f"\n{len(results)} player(s) found:\n")

        for i, player in enumerate(results, 1):
            name = player.get('name', player.get('firstname', 'N/A'))
            lastname = player.get('lastname', '')
            if lastname:
                name = f"{name} {lastname}".strip()

            club = player.get('club', player.get('clubName', 'N/A'))
            ttr = player.get('ttr', 'N/A')
            user_id = player.get('user_id', player.get('personId', 'N/A'))

            print(f"{i}. {name}")
            print(f"   Club: {club}")
            print(f"   TTR: {ttr}")
            print(f"   User-ID: {user_id}")
            print()

        # Save results to CSV
        self._save_search_results_csv(results, query)

    def _save_search_results_csv(self, results: List[Dict[str, Any]], query: str) -> None:
        """Save search results to CSV"""
        filename = f"search_{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self.tables_dir / filename

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SEARCH_RESULTS_FIELDS, extrasaction='ignore')
            writer.writeheader()
            for player in results:
                writer.writerow(player)

        print(f"\n✓ Saved results to {filepath}")

    def run_search_mode(self) -> None:
        """Run interactive search mode"""
        print("\n" + "="*60)
        print(" Player Search Mode")
        print("="*60)

        while True:
            query = input("\nEnter search query (or 'q' to quit): ").strip()

            if query.lower() == 'q':
                print("Exiting search mode...")
                break

            if not query:
                continue

            print("\nSearch method:")
            print("  1. API search (fast)")
            print("  2. Playwright search (reliable, shows page)")
            method = input("\nSelect method [1/2]: ").strip()

            if method == '2':
                use_playwright = True
            else:
                use_playwright = False
                print("Using API search")

            # Search
            results = self.search_players(query, use_playwright=use_playwright)

            # Display results
            if results:
                self._display_search_results(results, query)

                # Ask if user wants to fetch a player
                fetch_choice = input("\nFetch data for a player? (enter number or 'n'): ").strip()

                if fetch_choice.lower() != 'n':
                    try:
                        index = int(fetch_choice) - 1
                        if 0 <= index < len(results):
                            player = results[index]
                            user_id = player.get('user_id', player.get('personId'))
                            if user_id:
                                print(f"\nFetching data for: {player.get('name', user_id)}")
                                self.run_external_profile(user_id)
                            else:
                                print("\n⚠ No user-id found for this player")
                    except (ValueError, IndexError):
                        print("Invalid selection")
            else:
                print("\n⚠ No players found")

    def run_search_and_fetch_mode(self) -> None:
        """Run search and fetch selected players"""
        print("\n" + "="*60)
        print(" Search and Fetch Mode")
        print("="*60)

        query = input("\nEnter search query: ").strip()
        if not query:
            print("No query provided")
            return

        print("\nSearch method:")
        print("  1. API search")
        print("  2. Playwright search")
        method = input("\nSelect method [1/2]: ").strip()
        use_playwright = (method == '2')

        # Search
        results = self.search_players(query, use_playwright=use_playwright)

        if not results:
            print("\n⚠ No players found")
            return

        # Display results
        self._display_search_results(results, query)

        # Ask which players to fetch
        print("\n" + "-"*60)
        print(" Select players to fetch (comma-separated numbers, or 'all'):")
        selection = input("\nSelection: ").strip()

        if selection.lower() == 'all':
            # Fetch all
            indices = list(range(len(results)))
        else:
            # Parse selection
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                # Validate
                indices = [i for i in indices if 0 <= i < len(results)]
            except ValueError:
                print("Invalid selection")
                return

        # Fetch selected players
        print(f"\nFetching {len(indices)} player(s)...\n")

        for i, index in enumerate(indices, 1):
            player = results[index]
            user_id = player.get('user_id', player.get('personId'))

            if user_id:
                print(f"\n[{i}/{len(indices)}] Fetching: {player.get('name', user_id)}")
                prefix = f"search_{index}_"
                self.run_external_profile(user_id, prefix=prefix)

                if i < len(indices):
                    time.sleep(1)
            else:
                print(f"\n⚠ Skipping: {player.get('name', 'No name')} - no user-id")

        print("\n" + "="*60)
        print(f"✓ Completed fetching {len(indices)} player(s)")
        print("="*60)
