#!/usr/bin/env python3
"""
Debug script to explore the JSON structure.
"""

import json


def parse_multipart_json(file_content):
    """Parse a file that may contain JSON followed by other data"""
    brace_count = 0
    in_string = False
    escape_next = False
    json_end = -1

    for i, char in enumerate(file_content):
        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

    json_str = file_content[:json_end]
    return json.loads(json_str)


# Read the file
with open('community_response.json', 'r', encoding='utf-8') as f:
    file_content = f.read()

# Parse the JSON
data = parse_multipart_json(file_content)

print("=== Top-level keys ===")
for key in data.keys():
    print(f"  - {key}")

# Check pageContent
if 'pageContent' in data:
    page = data['pageContent']
    print(f"\n=== pageContent keys ===")
    for key in page.keys():
        print(f"  - {key}")

    if 'blockLoaderData' in page:
        print(f"\n=== blockLoaderData blocks ===")
        for block_id, block_data in page['blockLoaderData'].items():
            print(f"\nBlock ID: {block_id[:50]}...")
            if isinstance(block_data, dict):
                print(f"  Keys: {list(block_data.keys())}")

                if 'clubTtrRanking' in block_data:
                    print(f"  ✓ HAS clubTtrRanking ({len(block_data['clubTtrRanking'])} entries)")

                if 'teamLeagueRanking' in block_data:
                    print(f"  ✓ HAS teamLeagueRanking ({len(block_data['teamLeagueRanking'])} entries)")

# Also check the deferred data for TTR history
if '617005c9-dab5-4f43-aa5d-bd6c3b174899|data' in data:
    deferred_data = data['617005c9-dab5-4f43-aa5d-bd6c3b174899|data']
    print(f"\n=== Deferred TTR data ===")
    print(f"Type: {type(deferred_data)}")
    if isinstance(deferred_data, str) and deferred_data.startswith('__deferred_promise'):
        print(f"  Data is a deferred promise (not loaded yet)")
    elif isinstance(deferred_data, dict):
        print(f"  Keys: {list(deferred_data.keys())}")
