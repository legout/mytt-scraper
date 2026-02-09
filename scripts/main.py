#!/usr/bin/env python3
"""
Main entry point for MyTischtennis.de Scraper
"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

import getpass

from mytt_scraper import MyTischtennisScraper


def main():
    print("=== MyTischtennis.de Scraper ===\n")

    # Get credentials
    username = input("Username (email): ").strip()
    password = getpass.getpass("Password: ").strip()

    # Ask for mode
    print("\nSelect mode:")
    print("  1. Own profile")
    print("  2. External profile (by user-id)")
    print("  3. Multiple profiles")
    print("  4. Search for players")
    print("  5. Search and fetch")
    mode = input("\nMode [1-5]: ").strip()

    if not username or not password:
        print("Error: Username and password are required!")
        return

    # Ask if user wants headed mode
    headed_input = input("Run in headed mode? (shows browser window) [y/N]: ").strip().lower()
    headless = not headed_input.startswith('y')

    # Create scraper
    scraper = MyTischtennisScraper(username, password, headless=headless)

    if mode == '1':
        # Own profile
        result = scraper.run_own_profile()
        print("\n✓ Own profile data extracted!")
    elif mode == '2':
        # External profile
        user_id = input("Enter user-id: ").strip()
        prefix = input("Enter file prefix (optional, press Enter to use user-id): ").strip() or None
        result = scraper.run_external_profile(user_id, prefix)
        print(f"\n✓ External profile data extracted for {user_id}!")
    elif mode == '3':
        # Multiple profiles
        user_ids_input = input("Enter user-ids (comma-separated): ").strip()
        user_ids = [uid.strip() for uid in user_ids_input.split(',') if uid.strip()]
        if not user_ids:
            print("Error: No user-ids provided")
            return
        results = scraper.run_multiple_profiles(user_ids)
        print(f"\n✓ Data extracted for {len(user_ids)} profiles!")
    elif mode == '4':
        # Search for players
        scraper.run_search_mode()
    elif mode == '5':
        # Search and fetch
        scraper.run_search_and_fetch_mode()
    else:
        print("Invalid mode selected")
        return


if __name__ == "__main__":
    main()
