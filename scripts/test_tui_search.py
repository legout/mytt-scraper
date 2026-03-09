#!/usr/bin/env python3
"""Test the exact TUI search flow."""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from mytt_scraper import PlayerSearcher

# Credentials
USERNAME = "volker@lorrmann.de"
PASSWORD = "s78anwg9"

def test_tui_search_flow():
    """Test the exact flow the TUI uses."""
    print("="*60)
    print("Testing TUI Search Flow")
    print("="*60)
    
    # Step 1: Create searcher (like LoginScreen does)
    print("\n1. Creating PlayerSearcher (like LoginScreen)...")
    scraper = PlayerSearcher(USERNAME, PASSWORD, headless=True)
    print("   ✓ Searcher created")
    
    # Step 2: Login
    print("\n2. Calling login()...")
    if not scraper.login():
        print("   ✗ Login failed!")
        return False
    print("   ✓ Login successful")
    
    # Step 3: Search (like SearchScreen does)
    print("\n3. Calling search_players (like SearchScreen)...")
    query = "Müller"
    use_playwright = False
    
    print(f"   Query: '{query}'")
    print(f"   Use Playwright: {use_playwright}")
    
    # Check if session has cookies
    print(f"   Session cookies: {len(scraper.session.cookies)} cookies")
    
    results = scraper.search_players(query, use_playwright=use_playwright)
    
    print(f"\n   Results: {len(results)} players found")
    
    if results:
        print("\n   First 3 players:")
        for i, player in enumerate(results[:3], 1):
            print(f"     {i}. {player.get('name')} ({player.get('user_id')})")
        return True
    else:
        print("   ✗ No players found!")
        return False

if __name__ == "__main__":
    try:
        success = test_tui_search_flow()
        print("\n" + "="*60)
        if success:
            print("✓ TUI search flow works!")
        else:
            print("✗ TUI search flow failed!")
        print("="*60)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
