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
        """Try to search via API endpoints"""
        search_endpoints = [
            {
                'url': f"{COMMUNITY_URL}?search={query}&show=everything&_data=routes%2F%24",
                'name': 'Community search'
            },
        ]

        for endpoint in search_endpoints:
            print(f"Trying API: {endpoint['name']}")
            try:
                response = self.session.get(endpoint['url'])
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Look for players in response
                        if isinstance(data, dict):
                            # Check blockLoaderData
                            if 'pageContent' in data:
                                players = self._extract_players_from_page(data['pageContent'])
                                if players:
                                    print(f"✓ Found {len(players)} player(s) via API")
                                    return players

                        # Check other possible structures
                        for key in ['players', 'results', 'items', 'searchResults']:
                            if key in data and isinstance(data[key], list):
                                print(f"✓ Found {len(data[key])} player(s) via API")
                                return [self._parse_player_item(item) for item in data[key]]

                    except Exception:
                        # Try HTML parsing
                        players = self._extract_players_from_html(response.text)
                        if players:
                            print(f"✓ Extracted {len(players)} player(s) from HTML")
                            return players
            except requests.RequestException:
                continue

        return []

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
        """Use Playwright to interact with search UI"""
        print("Using Playwright for search...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='de-DE',
            )

            # Use existing cookies
            cookies = [{'name': c.name, 'value': c.value, 'domain': '.mytischtennis.de'} for c in self.session.cookies]
            await context.add_cookies(cookies)

            page = await context.new_page()

            try:
                await page.goto(f"{BASE_URL}/community", wait_until='networkidle')

                # Look for search input
                search_input = None

                for selector in SEARCH_INPUT_SELECTORS:
                    try:
                        element = page.locator(selector).first
                        if await element.is_visible(timeout=2000):
                            search_input = element
                            print(f"✓ Found search input: {selector}")
                            break
                    except:
                        continue

                if search_input:
                    await search_input.fill(query)
                    await asyncio.sleep(1)
                    await page.keyboard.press('Enter')
                    await page.wait_for_load_state('networkidle', timeout=5000)

                    html = await page.content()
                    players = self._extract_players_from_html(html)

                    await browser.close()
                    print(f"✓ Found {len(players)} player(s) via Playwright")
                    return players

            except Exception as e:
                print(f"Error during Playwright search: {e}")
                await browser.close()
                return []

        return []

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
