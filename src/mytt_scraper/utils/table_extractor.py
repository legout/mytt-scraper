"""Table extraction utilities for mytt_scraper"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

from ..config import (
    CLUB_INFO_FIELDS,
    TTR_RANKING_FIELDS,
    LEAGUE_TABLE_FIELDS,
    TTR_HISTORY_EVENTS_FIELDS,
    TTR_HISTORY_MATCHES_FIELDS,
)


def write_csv(data: List[Dict[str, Any]], filepath: Path, fieldnames: List[str]) -> None:
    """
    Write data to CSV file.

    Args:
        data: List of dictionaries to write
        filepath: Path to the output file
        fieldnames: List of field names for the CSV header
    """
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ Created {filepath} ({len(data)} rows)")


# =============================================================================
# In-Memory Extraction Helpers (return rows + fieldnames without writing CSV)
# =============================================================================


def get_club_info_rows(block_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Extract club info rows for in-memory use.

    Args:
        block_data: Block data containing club information

    Returns:
        Tuple of (rows, fieldnames) where rows is a list of dicts
    """
    club_info = {
        'clubNr': block_data.get('clubNr'),
        'association': block_data.get('association'),
        'season': block_data.get('season'),
        'group_name': block_data.get('group_name'),
        'group_name_short': block_data.get('group_name_short'),
        'group_id': block_data.get('group_id'),
        'extracted_at': datetime.now().isoformat(),
    }

    fieldnames = list(club_info.keys())
    return [club_info], fieldnames


def get_ttr_rankings_rows(block_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Extract TTR rankings rows for in-memory use.

    Args:
        block_data: Block data containing TTR rankings

    Returns:
        Tuple of (rows, fieldnames) where rows is a list of dicts
    """
    ttr_rankings = block_data.get('clubTtrRanking', [])
    return ttr_rankings, list(TTR_RANKING_FIELDS)


def get_league_table_rows(block_data: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Extract league table rows for in-memory use.

    Args:
        block_data: Block data containing league rankings

    Returns:
        Tuple of (rows, fieldnames) where rows is a list of dicts
    """
    teams = block_data.get('teamLeagueRanking', [])

    # Add season info from block_data
    season_info = {
        'season': block_data.get('season'),
        'league': block_data.get('group_name_short'),
        'group_id': block_data.get('group_id')
    }

    teams_with_season = [{**season_info, **team} for team in teams]
    return teams_with_season, list(LEAGUE_TABLE_FIELDS)


def get_ttr_history_events_rows(history: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Extract TTR history events rows for in-memory use.

    Args:
        history: History data containing events

    Returns:
        Tuple of (rows, fieldnames) where rows is a list of dicts
    """
    events = history.get('event', [])
    return events, list(TTR_HISTORY_EVENTS_FIELDS)


def get_ttr_history_matches_rows(history: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Extract TTR history matches rows for in-memory use.

    Args:
        history: History data containing events with matches

    Returns:
        Tuple of (rows, fieldnames) where rows is a list of dicts
    """
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

    return all_matches, list(TTR_HISTORY_MATCHES_FIELDS)


def extract_club_info_table(
    block_data: Dict[str, Any],
    tables_dir: Path,
    prefix: str = ''
) -> None:
    """
    Extract and save club info table.

    Args:
        block_data: Block data containing club information
        tables_dir: Directory to save tables
        prefix: Optional filename prefix
    """
    rows, fieldnames = get_club_info_rows(block_data)

    filename = f"{prefix}club_info.csv" if prefix else "club_info.csv"
    filepath = tables_dir / filename

    write_csv(rows, filepath, fieldnames)


def extract_ttr_rankings_table(
    block_data: Dict[str, Any],
    tables_dir: Path,
    prefix: str = ''
) -> None:
    """
    Extract and save TTR rankings table.

    Args:
        block_data: Block data containing TTR rankings
        tables_dir: Directory to save tables
        prefix: Optional filename prefix
    """
    rows, fieldnames = get_ttr_rankings_rows(block_data)

    filename = f"{prefix}ttr_rankings.csv" if prefix else "ttr_rankings.csv"
    filepath = tables_dir / filename

    write_csv(rows, filepath, fieldnames)


def extract_league_table(
    block_data: Dict[str, Any],
    tables_dir: Path,
    prefix: str = ''
) -> None:
    """
    Extract and save league table.

    Args:
        block_data: Block data containing league rankings
        tables_dir: Directory to save tables
        prefix: Optional filename prefix
    """
    rows, fieldnames = get_league_table_rows(block_data)

    filename = f"{prefix}league_table.csv" if prefix else "league_table.csv"
    filepath = tables_dir / filename

    write_csv(rows, filepath, fieldnames)


def extract_ttr_history_events_table(
    history: Dict[str, Any],
    tables_dir: Path,
    prefix: str = ''
) -> None:
    """
    Extract and save TTR history events table.

    Args:
        history: History data containing events
        tables_dir: Directory to save tables
        prefix: Optional filename prefix
    """
    rows, fieldnames = get_ttr_history_events_rows(history)

    filename = f"{prefix}ttr_history_events.csv" if prefix else "ttr_history_events.csv"
    filepath = tables_dir / filename

    write_csv(rows, filepath, fieldnames)


def extract_ttr_history_matches_table(
    history: Dict[str, Any],
    tables_dir: Path,
    prefix: str = ''
) -> None:
    """
    Extract and save TTR history matches table.

    Args:
        history: History data containing events with matches
        tables_dir: Directory to save tables
        prefix: Optional filename prefix
    """
    rows, fieldnames = get_ttr_history_matches_rows(history)

    filename = f"{prefix}ttr_history_matches.csv" if prefix else "ttr_history_matches.csv"
    filepath = tables_dir / filename

    write_csv(rows, filepath, fieldnames)
