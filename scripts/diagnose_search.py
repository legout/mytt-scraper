#!/usr/bin/env python3
"""Diagnose script to understand why search isn't working."""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

import requests
from mytt_scraper import PlayerSearcher
from mytt_scraper.config import BASE_URL

# Credentials
USERNAME = "volker@lorrmann.de"
PASSWORD = "s78anwg9"

def diagnose_search():
    """Diagnose the search functionality step by step."""
    print("="*60)
    print("Search Diagnostics")
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
    
    # Check session cookies
    print("\n3. Checking session cookies...")
    print(f"  Session cookies: {dict(searcher.session.cookies)}")
    print(f"  Cookie names: {list(searcher.session.cookies.keys())}")
    
    # Check session headers
    print("\n4. Checking session headers...")
    print(f"  Session headers: {dict(searcher.session.headers)}")
    
    # Try direct API call with detailed debugging
    print("\n5. Testing direct API call...")
    search_url = f"{BASE_URL}/api/search/players"
    data = {
        'query': 'Müller',
        'page': '1',
        'pagesize': '10'
    }
    
    print(f"  URL: {search_url}")
    print(f"  Data: {data}")
    print(f"  Cookies: {searcher.session.cookies.get_dict()}")
    
    try:
        response = searcher.session.post(search_url, data=data)
        print(f"\n  Response status: {response.status_code}")
        print(f"  Response headers: {dict(response.headers)}")
        print(f"  Response URL: {response.url}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n  Response JSON keys: {list(result.keys())}")
                
                if 'results' in result:
                    players = result['results']
                    print(f"  Number of results: {len(players)}")
                    
                    if players:
                        print("\n  First player:")
                        print(f"    {players[0]}")
                    else:
                        print("\n  ⚠ Results array is empty!")
                else:
                    print(f"\n  ⚠ No 'results' key in response!")
                    print(f"  Full response: {result}")
            except Exception as e:
                print(f"\n  ✗ JSON parse error: {e}")
                print(f"  Response text: {response.text[:500]}")
        else:
            print(f"\n  ✗ Non-200 status code!")
            print(f"  Response text: {response.text[:500]}")
            
    except Exception as e:
        print(f"\n  ✗ Request error: {e}")
        import traceback
        traceback.print_exc()
    
    # Now try using the actual search method with debugging
    print("\n6. Testing via search_players method...")
    print("  Calling searcher.search_players('Müller', use_playwright=False)")
    
    # Patch the method to add debugging
    original_search = searcher._search_via_api
    
    def debug_search(query):
        print(f"\n  [DEBUG] _search_via_api called with query: '{query}'")
        results = original_search(query)
        print(f"  [DEBUG] _search_via_api returned {len(results)} results")
        return results
    
    searcher._search_via_api = debug_search
    
    results = searcher.search_players("Müller", use_playwright=False)
    print(f"\n  Final result count: {len(results)}")
    
    if results:
        print("\n  First result:")
        print(f"    {results[0]}")
    else:
        print("\n  ⚠ No results returned!")
    
    return True

if __name__ == "__main__":
    try:
        diagnose_search()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
