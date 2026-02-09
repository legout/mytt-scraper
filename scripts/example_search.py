#!/usr/bin/env python3
"""Example script for searching players"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from mytt_scraper import PlayerSearcher


def main():
    # Create searcher
    searcher = PlayerSearcher("your@email.com", "password")

    # Login
    if searcher.login():
        # Search for players
        results = searcher.search_players("Müller", use_playwright=False)

        print(f"Found {len(results)} players")
        for player in results:
            print(f"  - {player.get('name')}: {player.get('club')} (TTR: {player.get('ttr')})")

        # Optionally fetch a specific player
        if results and results[0].get('user_id'):
            user_id = results[0]['user_id']
            print(f"\nFetching data for {results[0].get('name')}...")
            searcher.run_external_profile(user_id)
    else:
        print("Login failed")


if __name__ == "__main__":
    main()
