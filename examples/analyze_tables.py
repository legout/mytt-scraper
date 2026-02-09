#!/usr/bin/env python3
"""
Script to analyze and query the TTR tables.
Demonstrates data relationships and useful queries.
"""

import pandas as pd
from pathlib import Path


def load_tables(tables_dir='tables'):
    """Load all CSV tables into pandas DataFrames"""
    return {
        'club_info': pd.read_csv(f'{tables_dir}/club_info.csv'),
        'ttr_rankings': pd.read_csv(f'{tables_dir}/ttr_rankings.csv'),
        'league_table': pd.read_csv(f'{tables_dir}/league_table.csv'),
        'ttr_history_events': pd.read_csv(f'{tables_dir}/ttr_history_events.csv'),
        'ttr_history_matches': pd.read_csv(f'{tables_dir}/ttr_history_matches.csv'),
    }


def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def main():
    print("="*70)
    print(" TTR DATA ANALYSIS")
    print("="*70)

    # Load tables
    print("\nLoading tables...")
    dfs = load_tables()

    # 1. Club Information
    print_section("1. Club Information")
    club_info = dfs['club_info'].iloc[0]
    print(f"Club: {club_info['name'] or 'N/A'} (Nr: {club_info['clubNr']})")
    print(f"Association: {club_info['association']}")
    print(f"Season: {club_info['season']}")
    print(f"League: {club_info['group_name_short']}")
    print(f"Full League: {club_info['group_name']}")
    print(f"Data Extracted: {club_info['extracted_at']}")

    # 2. Player Rankings
    print_section("2. Player Rankings (by TTR)")
    rankings = dfs['ttr_rankings'].sort_values('rank')
    print(f"\n{'Position':>8} {'Name':<25} {'TTR':>10} {'Matches':>8}")
    print("-" * 70)
    for _, row in rankings.iterrows():
        name = f"{row['firstname']} {row['lastname']}"
        print(f"{row['position']:>8} {name:<25} {row['rank']:>10,} {row['matchCount']:>8}")

    # 3. League Standings
    print_section("3. League Table")
    league = dfs['league_table'].sort_values('table_rank')
    print(f"\n{'Rank':>5} {'Team':<30} {'Points':>8} {'Trend':>6}")
    print("-" * 70)
    for _, row in league.iterrows():
        trend = row['tendency']
        icon = "↑" if trend == 'rise' else "↓" if trend == 'fall' else "→"
        print(f"{row['table_rank']:>5} {row['teamname']:<30} {row['own_points']:>8}   {icon}")

    # 4. TTR History Summary
    print_section("4. TTR History Summary")
    events = dfs['ttr_history_events']
    events['event_date'] = pd.to_datetime(events['event_date_time'])

    # Calculate stats
    total_events = len(events)
    total_ttr_change = events['ttr_delta'].sum()
    ttr_start = events['ttr_before'].iloc[-1] if len(events) > 0 else 0
    ttr_end = events['ttr_after'].iloc[0] if len(events) > 0 else 0

    events_won = events[events['ttr_delta'] > 0]
    events_lost = events[events['ttr_delta'] < 0]

    print(f"\nTotal Events: {total_events}")
    print(f"TTR Range: {ttr_start:,} → {ttr_end:,} (change: {total_ttr_change:+,})")
    print(f"Events with TTR gain: {len(events_won)}")
    print(f"Events with TTR loss: {len(events_lost)}")

    # Date range
    earliest = events['event_date'].min()
    latest = events['event_date'].max()
    print(f"Date Range: {earliest.strftime('%d.%m.%Y')} → {latest.strftime('%d.%m.%Y')}")

    # 5. Recent Matches (with detailed data)
    print_section("5. Recent Matches (with detailed scores)")

    matches = dfs['ttr_history_matches']
    if len(matches) > 0:
        # Sort by most recent
        matches_sorted = matches.sort_values('event_date_time', ascending=False).head(10)

        print(f"\n{'Date':>12} {'Opponent':<25} {'Score':>20} {'TTR':>8}")
        print("-" * 70)

        for _, match in matches_sorted.iterrows():
            # Calculate set score
            sets_won = match['own_sets']
            sets_lost = match['other_sets']

            # Build score string
            score_parts = []
            for i in range(1, 8):
                own = match.get(f'own_set{i}', 0)
                other = match.get(f'other_set{i}', 0)
                if pd.notna(own) and pd.notna(other) and (own > 0 or other > 0):
                    score_parts.append(f"{int(own)}:{int(other)}")

            score = " ".join(score_parts) if score_parts else f"{sets_won}:{sets_lost}"
            opponent = match['other_person_name'] if pd.notna(match['other_person_name']) else match['other_team_name']
            date = match['formattedEventDate']

            result = "W" if match['own_sets'] > match['other_sets'] else "L"
            print(f"{date:>12} {opponent:<25} {score:>20}  {result:>1}")
    else:
        print("\nNo detailed match data available.")

    # 6. Recent Events Summary
    print_section("6. Recent Events (Last 10)")

    events_sorted = events.sort_values('event_date', ascending=False).head(10)
    print(f"\n{'Date':>12} {'Event':<50} {'Δ TTR':>8}")
    print("-" * 70)

    for _, event in events_sorted.iterrows():
        delta = event['ttr_delta']
        delta_str = f"{delta:+,}" if delta != 0 else "-"
        event_short = event['event_name'][:48] + ".." if len(event['event_name']) > 50 else event['event_name']
        print(f"{event['formattedEventDate']:>12} {event_short:<50} {delta_str:>8}")

    # 7. Best & Worst Performances
    print_section("7. Best & Worst TTR Changes")

    best_events = events.nlargest(5, 'ttr_delta')
    worst_events = events.nsmallest(5, 'ttr_delta')

    print("\nBest Gains:")
    for _, event in best_events.iterrows():
        print(f"  {event['ttr_delta']:+4d} | {event['formattedEventDate']} | {event['event_name'][:50]}")

    print("\nWorst Losses:")
    for _, event in worst_events.iterrows():
        print(f"  {event['ttr_delta']:+4d} | {event['formattedEventDate']} | {event['event_name'][:50]}")

    # 8. Match Statistics
    print_section("8. Match Statistics")

    total_matches = events['match_count'].sum()
    matches_won = events['matches_won'].sum()
    matches_lost = events['matches_lost'].sum()

    win_rate = (matches_won / total_matches * 100) if total_matches > 0 else 0

    print(f"\nTotal Matches: {total_matches}")
    print(f"Matches Won: {matches_won} ({win_rate:.1f}%)")
    print(f"Matches Lost: {matches_lost}")

    # Count event types
    type_counts = events['type'].value_counts()
    print(f"\nEvent Types:")
    for event_type, count in type_counts.items():
        print(f"  {event_type}: {count}")

    print("\n" + "="*70)
    print(" Analysis Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
