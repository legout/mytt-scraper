#!/usr/bin/env python3
"""
Script to create flat tables (CSV) from ttr_data.json
"""

import json
import csv
from pathlib import Path


def load_ttr_data(json_file='ttr_data.json'):
    """Load TTR data from JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_csv(data, filename, fieldnames):
    """Write data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ Created {filename} ({len(data)} rows)")


def create_club_info_table(data, output_dir='tables'):
    """Create club info table"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    club_info = data['club_info']
    club_info['extracted_at'] = data['extracted_at']

    # Flatten to single row
    row = {k: str(v) if v is not None else '' for k, v in club_info.items()}
    fieldnames = list(club_info.keys())

    filename = output_dir / 'club_info.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)
    print(f"✓ Created {filename} (1 row)")


def create_ttr_rankings_table(data, output_dir='tables'):
    """Create TTR rankings table"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    fieldnames = [
        'position', 'firstname', 'lastname', 'rank', 'germanRank', 'clubSexRank',
        'germanSexRank', 'fedRank', 'clubName', 'clubNr', 'personId',
        'matchCount', 'fewGames', 'gender', 'country', 'continent',
        'fedNickname', 'external_id', 'lastYearNoGames'
    ]

    write_csv(data['ttr_rankings'], output_dir / 'ttr_rankings.csv', fieldnames)


def create_league_table(data, output_dir='tables'):
    """Create league standings table"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    fieldnames = [
        'table_rank', 'teamname', 'club_nr', 'team_id',
        'own_points', 'other_points', 'tendency'
    ]

    # Add season info from club_info
    club_info = data['club_info']
    season_info = {
        'season': club_info['season'],
        'league': club_info['group_name_short'],
        'group_id': club_info['group_id']
    }

    # Add season info to each team row
    teams = []
    for team in data['league_table']:
        team_row = {**season_info, **team}
        teams.append(team_row)

    fieldnames_extended = ['season', 'league', 'group_id'] + fieldnames
    write_csv(teams, output_dir / 'league_table.csv', fieldnames_extended)


def create_ttr_history_events_table(data, output_dir='tables'):
    """Create TTR history events table (one row per event)"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Extract history data
    history_data = data.get('ttr_history', {})
    if not history_data:
        print("⚠ No TTR history data found")
        return

    # The history is nested under a key like "617005c9-dab5-4f43-aa5d-bd6c3b174899|data"
    # Find the key that contains 'ttr' and 'event'
    events_key = None
    for key in history_data.keys():
        if isinstance(history_data[key], dict) and 'ttr' in history_data[key]:
            events_key = key
            break

    if not events_key:
        print("⚠ No events found in TTR history")
        return

    history = history_data[events_key]
    events = history.get('event', [])

    fieldnames = [
        'event_date_time', 'formattedEventDate', 'formattedEventTime',
        'event_name', 'event_id', 'type',
        'ttr_before', 'ttr_after', 'ttr_delta',
        'match_count', 'matches_won', 'matches_lost',
        'expected_result', 'alteration_constant'
    ]

    write_csv(events, output_dir / 'ttr_history_events.csv', fieldnames)


def create_ttr_history_matches_table(data, output_dir='tables'):
    """Create TTR history matches table (one row per match)"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Extract history data
    history_data = data.get('ttr_history', {})
    if not history_data:
        return

    # Find events
    events_key = None
    for key in history_data.keys():
        if isinstance(history_data[key], dict) and 'ttr' in history_data[key]:
            events_key = key
            break

    if not events_key:
        return

    history = history_data[events_key]
    events = history.get('event', [])

    # Flatten all matches from all events
    all_matches = []

    for event in events:
        event_info = {
            'event_id': event.get('event_id'),
            'event_name': event.get('event_name'),
            'event_date_time': event.get('event_date_time'),
            'formattedEventDate': event.get('formattedEventDate'),
            'formattedEventTime': event.get('formattedEventTime'),
            'event_type': event.get('type'),
            'ttr_before': event.get('ttr_before'),
            'ttr_after': event.get('ttr_after'),
        }

        matches = event.get('match', [])
        if isinstance(matches, list):
            for i, match in enumerate(matches, 1):
                match_row = {**event_info, 'match_number': i, **match}
                all_matches.append(match_row)

    fieldnames = [
        'event_id', 'event_name', 'event_date_time', 'formattedEventDate', 'formattedEventTime',
        'event_type', 'match_number', 'type',
        'own_person_id', 'own_person_name', 'own_team_name', 'own_ttr',
        'other_person_id', 'other_person_name', 'other_team_name', 'other_ttr',
        'ttr_before', 'ttr_after', 'scheduled', 'expected_result',
        'own_set1', 'own_set2', 'own_set3', 'own_set4', 'own_set5', 'own_set6', 'own_set7',
        'other_set1', 'other_set2', 'other_set3', 'other_set4', 'other_set5', 'other_set6', 'other_set7',
        'own_sets', 'other_sets', 'own_points', 'other_points', 'other_w_r_l'
    ]

    write_csv(all_matches, output_dir / 'ttr_history_matches.csv', fieldnames)


def create_tournament_registrations_table(data, output_dir='tables'):
    """Create tournament registrations table"""
    # This would come from the community response if needed
    # Not currently in ttr_data.json but could be added
    pass


def main():
    print("="*60)
    print("Creating flat tables from ttr_data.json")
    print("="*60)

    # Load data
    data = load_ttr_data()

    # Create tables
    print("\n--- Creating Tables ---\n")

    # 1. Club Info
    create_club_info_table(data)

    # 2. TTR Rankings
    create_ttr_rankings_table(data)

    # 3. League Table
    create_league_table(data)

    # 4. TTR History Events
    create_ttr_history_events_table(data)

    # 5. TTR History Matches
    create_ttr_history_matches_table(data)

    print("\n" + "="*60)
    print("✓ All tables created in 'tables/' directory")
    print("="*60)


if __name__ == "__main__":
    main()
