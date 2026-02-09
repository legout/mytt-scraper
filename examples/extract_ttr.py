#!/usr/bin/env python3
"""
Script to parse the community response and extract TTR data.
Handles multipart JSON responses.
"""

import json
import re
from datetime import datetime


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
    remaining = file_content[json_end:]

    return json.loads(json_str), remaining


def parse_deferred_data(remaining):
    """Parse the deferred data from the remaining content"""

    # Look for data:{"617005c9-dab5-4f43-aa5d-bd6c3b174899|data": {...}}
    # This is the actual TTR history data

    # Try to find the data: pattern
    data_match = re.search(r'data:\{("[^"]+":\{.*?\}|"[^"]+":"[^"]*")\}', remaining, re.DOTALL)

    if not data_match:
        return None

    try:
        # Extract the data part
        data_str = 'data:{' + data_match.group(1) + '}'
        # Parse as JSON
        return json.loads('{' + data_match.group(1) + '}')
    except:
        return None


def extract_ttr_data(json_file='community_response.json', output_file='ttr_data.json'):
    """Extract TTR data from the community response JSON"""

    # Read the file
    with open(json_file, 'r', encoding='utf-8') as f:
        file_content = f.read()

    # Parse the multipart response
    try:
        data, remaining = parse_multipart_json(file_content)
        print(f"✓ Successfully parsed JSON (size: {len(str(data))} chars)")
        print(f"Remaining data: {len(remaining)} chars")
    except Exception as e:
        print(f"✗ Error parsing JSON: {e}")
        return None

    # Extract TTR ranking data from blockLoaderData in pageContent
    ttr_data = None
    club_info = None
    league_info = None
    ttr_history = None

    if 'pageContent' in data and 'blockLoaderData' in data['pageContent']:
        block_loader = data['pageContent']['blockLoaderData']

        # Look for the block containing clubTtrRanking
        for block_id, block_data in block_loader.items():
            if isinstance(block_data, dict) and 'clubTtrRanking' in block_data:
                print(f"\n✓ Found TTR data in block: {block_id[:50]}...")
                ttr_data = block_data['clubTtrRanking']
                club_info = block_data
                league_info = block_data.get('teamLeagueRanking', [])
                break

        # Also check for TTR history in deferred data
        ttr_history = parse_deferred_data(remaining)
        if ttr_history:
            print(f"✓ Found TTR history data")

    if not ttr_data:
        print("✗ No TTR ranking data found!")
        return None

    result = {
        'extracted_at': datetime.now().isoformat(),
        'club_info': {
            'name': club_info.get('clubName'),
            'clubNr': club_info.get('clubNr'),
            'association': club_info.get('association'),
            'season': club_info.get('season'),
            'group_name': club_info.get('group_name'),
            'group_name_short': club_info.get('group_name_short'),
            'group_id': club_info.get('group_id'),
        },
        'league_table': league_info,
        'ttr_rankings': ttr_data,
        'ttr_history': ttr_history,
    }

    # Save the extracted TTR data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Extracted {len(ttr_data)} TTR rankings")
    print(f"✓ Extracted {len(league_info)} league entries")
    if ttr_history:
        print(f"✓ Extracted TTR history")
    print(f"✓ Saved to {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("TTR RANKING SUMMARY")
    print("="*60)
    print(f"Club: {club_info.get('clubName')} ({club_info.get('clubNr')})")
    print(f"League: {club_info.get('group_name_short')}")
    print(f"Season: {club_info.get('season')}")
    print(f"\nTop Players:")
    for player in ttr_data:
        print(f"  {player['position']:2d}. {player['firstname']:15s} {player['lastname']:15s} - TTR: {player['rank']:,}")

    print(f"\nLeague Table:")
    for team in league_info:
        tendency_icon = "↑" if team['tendency'] == 'rise' else "→" if team['tendency'] == 'steady' else "↓"
        print(f"  {team['table_rank']:2d}. {team['teamname']:30s} ({team['own_points']} pts) {tendency_icon}")

    if ttr_history and 'ttr' in ttr_history:
        print(f"\nCurrent TTR: {ttr_history['ttr']}")

    return result


def print_detailed_ttr_data(result):
    """Print detailed information about TTR data"""
    print("\n" + "="*80)
    print("DETAILED TTR INFORMATION")
    print("="*80)

    info = result['club_info']
    print(f"\nClub Information:")
    print(f"  Name: {info['name']} (Nr: {info['clubNr']})")
    print(f"  Association: {info['association']}")
    print(f"  Season: {info['season']}")
    print(f"  League: {info['group_name']}")
    print(f"  League Short: {info['group_name_short']}")
    print(f"  Group ID: {info['group_id']}")

    print(f"\nLeague Table:")
    print("-" * 80)
    for team in result['league_table']:
        tendency_icon = "↑" if team['tendency'] == 'rise' else "→" if team['tendency'] == 'steady' else "↓"
        print(f"  {team['table_rank']:2d}. {team['teamname']:30s} ({team['own_points']}:{team['other_points']}) {tendency_icon}")

    print(f"\nTTR Rankings:")
    print("-" * 80)
    for idx, player in enumerate(result['ttr_rankings'], 1):
        print(f"\nPlayer #{idx}:")
        print(f"  Name: {player['firstname']} {player['lastname']}")
        print(f"  TTR Rank: {player['rank']:,}")
        print(f"  German Rank: {player['germanRank']:,}")
        print(f"  Club Position: {player['position']}")
        print(f"  Club Sex Rank: {player['clubSexRank']:,}")
        print(f"  German Sex Rank: {player['germanSexRank']:,}")
        print(f"  Federation Rank: {player['fedRank']}")
        print(f"  Club: {player['clubName']} (Nr: {player['clubNr']})")
        print(f"  Federation: {player['fedNickname']}")
        print(f"  Country: {player['country']}")
        print(f"  Continent: {player['continent']}")
        print(f"  Gender: {player['gender']}")
        print(f"  Match Count: {player['matchCount']}")
        print(f"  Few Games: {player['fewGames']}")
        print(f"  Person ID: {player['personId']}")
        print(f"  External ID: {player['external_id']}")

    if result['ttr_history']:
        print(f"\nTTR History:")
        print("-" * 80)
        print(f"Current TTR: {result['ttr_history'].get('ttr', 'N/A')}")
        if 'event' in result['ttr_history']:
            print(f"Number of events: {len(result['ttr_history']['event'])}")


if __name__ == "__main__":
    # Extract TTR data
    result = extract_ttr_data()

    if result:
        # Print detailed info
        print_detailed_ttr_data(result)
        print("\n✓ TTR data extraction complete!")
    else:
        print("\n✗ Failed to extract TTR data!")
