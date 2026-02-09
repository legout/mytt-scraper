#!/usr/bin/env python3
"""Test JSON parsing with existing data"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from mytt_scraper.utils import parse_multipart_json


def main():
    # Test with existing JSON file
    json_file = Path(__file__).parent.parent / 'community_response.json'

    if not json_file.exists():
        print(f"Error: {json_file} not found")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Test parsing
    print("Testing multipart JSON parsing...")
    print(f"Input length: {len(content)} characters")

    try:
        data, remaining = parse_multipart_json(content)
        print(f"✓ Successfully parsed JSON")
        print(f"  - Data keys: {list(data.keys())}")
        print(f"  - Remaining length: {len(remaining)} characters")

        # Check pageContent
        if 'pageContent' in data:
            print(f"  - pageContent found with keys: {list(data['pageContent'].keys())}")

    except Exception as e:
        print(f"✗ Error parsing: {e}")


if __name__ == "__main__":
    main()
