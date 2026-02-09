#!/usr/bin/env python3
"""Test login functionality"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from mytt_scraper import MyTischtennisScraper


def main():
    username = input("Username (email): ").strip()
    password = input("Password: ").strip()

    scraper = MyTischtennisScraper(username, password, headless=False)

    if scraper.login():
        print("✓ Login successful!")

        # Test fetching data
        print("\nTesting fetch_own_community...")
        data, remaining = scraper.fetch_own_community()
        if data:
            print(f"✓ Fetched data with keys: {list(data.keys())}")
        else:
            print("✗ Failed to fetch data")
    else:
        print("✗ Login failed")


if __name__ == "__main__":
    main()
