#!/usr/bin/env python3
"""Example script for fetching multiple players"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from mytt_scraper import MyTischtennisScraper


def main():
    # Create scraper
    scraper = MyTischtennisScraper("your@email.com", "password")

    # Login
    if scraper.login():
        # Fetch multiple profiles
        user_ids = [
            "2fa35076-e634-457c-bf70-e89a70e0b7b0",
            "another-user-id-here"
        ]

        results = scraper.run_multiple_profiles(user_ids)
        print(f"Fetched {len(results)} profiles")
    else:
        print("Login failed")


if __name__ == "__main__":
    main()
