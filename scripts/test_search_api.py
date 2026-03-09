#!/usr/bin/env python3
"""Test script to verify the search API works correctly."""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from mytt_scraper import PlayerSearcher

# Credentials
USERNAME = "volker@lorrmann.de"
PASSWORD = "s78anwg9"

def test_search():
    """Test the search functionality."""
    print("="*60)
    print("Testing mytischtennis.de Search API")
    print("="*60)
    
    # Create searcher
    print("\n1. Creating PlayerSearcher...")
    searcher = PlayerSearcher(USERNAME, PASSWORD, headless=True)
    
    # Login
    print("\n2. Logging in...")
    if not searcher.login():
        print("✗ Login failed!")
        return False
    print("✓ Login successful")
    
    # Test search
    print("\n3. Searching for 'Müller'...")
    results = searcher.search_players("Müller", use_playwright=False)
    
    print(f"\n✓ Found {len(results)} player(s):")
    print("-"*60)
    
    for i, player in enumerate(results[:10], 1):  # Show first 10
        name = player.get('name', 'Unknown')
        club = player.get('club', 'N/A')
        user_id = player.get('user_id', 'N/A')
        
        print(f"{i}. {name}")
        print(f"   Club: {club}")
        print(f"   User ID: {user_id}")
        print()
    
    if len(results) > 10:
        print(f"... and {len(results) - 10} more")
    
    # Test another search
    print("\n4. Searching for 'Schmidt'...")
    results2 = searcher.search_players("Schmidt", use_playwright=False)
    print(f"✓ Found {len(results2)} player(s)")
    
    print("\n" + "="*60)
    print("Search test completed successfully!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_search()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
