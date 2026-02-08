"""In-memory flat table extraction for mytt_scraper.

This module provides a public API for extracting structured tables from
scraped data as in-memory DataFrame/Table objects, without writing to CSV.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Literal, overload

from ..config import (
    CLUB_INFO_FIELDS,
    LEAGUE_TABLE_FIELDS,
    TTR_HISTORY_EVENTS_FIELDS,
    TTR_HISTORY_MATCHES_FIELDS,
    TTR_RANKING_FIELDS,
)

# Supported backend types
Backend = Literal["polars", "pandas", "pyarrow"]


def _extract_club_info_records(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract club info records from data.

    Args:
        data: Main response data

    Returns:
        List with single club info record, or None if not found
    """
    if "pageContent" not in data or "blockLoaderData" not in data["pageContent"]:
        return None

    block_loader = data["pageContent"]["blockLoaderData"]

    for block_data in block_loader.values():
        if not isinstance(block_data, dict):
            continue

        # Check for club info fields - require at least 2 matching fields
        club_info_fields = ["clubNr", "association", "season", "group_name"]
        matching_fields = sum(1 for f in club_info_fields if f in block_data)
        if matching_fields >= 2:
            club_info = {
                "clubNr": block_data.get("clubNr"),
                "association": block_data.get("association"),
                "season": block_data.get("season"),
                "group_name": block_data.get("group_name"),
                "group_name_short": block_data.get("group_name_short"),
                "group_id": block_data.get("group_id"),
                "extracted_at": datetime.now().isoformat(),
            }
            return [club_info]

    return None


def _extract_ttr_rankings_records(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract TTR rankings records from data.

    Args:
        data: Main response data

    Returns:
        List of TTR ranking records, or None if not found
    """
    if "pageContent" not in data or "blockLoaderData" not in data["pageContent"]:
        return None

    block_loader = data["pageContent"]["blockLoaderData"]

    for block_data in block_loader.values():
        if not isinstance(block_data, dict):
            continue

        if "clubTtrRanking" in block_data:
            rankings = block_data.get("clubTtrRanking", [])
            if rankings:
                return list(rankings)
            return []

    return None


def _extract_league_table_records(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract league table records from data.

    Args:
        data: Main response data

    Returns:
        List of league team records, or None if not found
    """
    if "pageContent" not in data or "blockLoaderData" not in data["pageContent"]:
        return None

    block_loader = data["pageContent"]["blockLoaderData"]

    for block_data in block_loader.values():
        if not isinstance(block_data, dict):
            continue

        if "teamLeagueRanking" in block_data:
            teams = block_data.get("teamLeagueRanking", [])

            # Add season info from block_data
            season_info = {
                "season": block_data.get("season"),
                "league": block_data.get("group_name_short"),
                "group_id": block_data.get("group_id"),
            }

            return [{**season_info, **team} for team in teams]

    return None


def _extract_ttr_history_from_remaining(remaining: str | None) -> dict[str, Any] | None:
    """Extract TTR history data from remaining text.

    Args:
        remaining: Remaining text containing deferred data

    Returns:
        History dict with 'event' and 'ttr' keys, or None if not found
    """
    if not remaining or "data:" not in remaining:
        return None

    try:
        # Find data: and extract everything after it
        data_start = remaining.find("data:") + 5
        data_str = remaining[data_start:].strip()

        # Try to parse the JSON
        parsed = json.loads(data_str)

        # Look for a key that contains ttr and event data
        for value in parsed.values():
            if isinstance(value, dict) and "ttr" in value and "event" in value:
                return value

    except json.JSONDecodeError:
        # Try alternative approach: find the nested JSON object
        try:
            nested_match = re.search(r'".*\|data":(\{.*\})\}', remaining)
            if nested_match:
                nested_json = nested_match.group(1)
                history = json.loads(nested_json)
                if "ttr" in history and "event" in history:
                    return history
        except Exception:
            pass

    return None


def _extract_ttr_history_events_records(
    history: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract TTR history events records from history data.

    Args:
        history: History data containing events

    Returns:
        List of event records
    """
    return list(history.get("event", []))


def _extract_ttr_history_matches_records(
    history: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract TTR history matches records from history data.

    Args:
        history: History data containing events with matches

    Returns:
        List of flattened match records
    """
    events = history.get("event", [])
    all_matches = []

    for event in events:
        event_info = {
            "event_id": event.get("event_id"),
            "event_name": event.get("event_name"),
            "event_date_time": event.get("event_date_time"),
            "formattedEventDate": event.get("formattedEventDate"),
            "formattedEventTime": event.get("formattedEventTime"),
            "event_type": event.get("type"),
            "ttr_before": event.get("ttr_before"),
            "ttr_after": event.get("ttr_after"),
        }

        matches = event.get("match", [])
        if isinstance(matches, list):
            for i, match in enumerate(matches, 1):
                match_row = {**event_info, "match_number": i, **match}
                all_matches.append(match_row)

    return all_matches


def _to_polars_df(records: list[dict[str, Any]], columns: list[str] | None = None):  # type: ignore[return]  # Conditional import, return type is polars.DataFrame
    """Convert records to Polars DataFrame with deterministic column order.

    Args:
        records: List of record dictionaries
        columns: Optional list of columns to enforce ordering

    Returns:
        polars.DataFrame
    """
    import polars as pl

    if not records:
        # Create empty DataFrame with correct schema
        schema = {col: pl.Utf8 for col in columns} if columns else {}
        return pl.DataFrame(schema)

    df = pl.DataFrame(records)

    if columns:
        # Reorder columns to match expected order
        existing_cols = [c for c in columns if c in df.columns]
        df = df.select(existing_cols)

    return df


def _to_pandas_df(records: list[dict[str, Any]], columns: list[str] | None = None):  # type: ignore[return]  # Conditional import, return type is pandas.DataFrame
    """Convert records to Pandas DataFrame with deterministic column order.

    Args:
        records: List of record dictionaries
        columns: Optional list of columns to enforce ordering

    Returns:
        pandas.DataFrame
    """
    import pandas as pd

    df = pd.DataFrame(records)

    if columns:
        # Ensure all expected columns exist
        for col in columns:
            if col not in df.columns:
                df[col] = None
        # Reorder columns
        df = df[columns]

    return df


def _to_pyarrow_table(records: list[dict[str, Any]], columns: list[str] | None = None):  # type: ignore[return]  # Conditional import, return type is pyarrow.Table
    """Convert records to PyArrow Table with deterministic column order.

    Args:
        records: List of record dictionaries
        columns: Optional list of columns to enforce ordering

    Returns:
        pyarrow.Table
    """
    import pyarrow as pa

    if not records:
        # Create empty table with correct schema
        schema_fields = [(col, pa.string()) for col in columns] if columns else []
        schema = pa.schema(schema_fields)
        return pa.Table.from_pydict({col: [] for col in columns or []}, schema=schema)

    # Create table from records
    table = pa.Table.from_pylist(records)

    if columns:
        # Reorder columns to match expected order
        existing_cols = [c for c in columns if c in table.column_names]
        table = table.select(existing_cols)

    return table


@overload
def extract_flat_tables(
    data: dict[str, Any],
    remaining: str | None = None,
    *,
    backend: Literal["polars"],
) -> dict[str, Any]: ...


@overload
def extract_flat_tables(
    data: dict[str, Any],
    remaining: str | None = None,
    *,
    backend: Literal["pandas"],
) -> dict[str, Any]: ...


@overload
def extract_flat_tables(
    data: dict[str, Any],
    remaining: str | None = None,
    *,
    backend: Literal["pyarrow"],
) -> dict[str, Any]: ...


def extract_flat_tables(
    data: dict[str, Any],
    remaining: str | None = None,
    *,
    backend: Backend = "polars",
) -> dict[str, Any]:
    """Extract flat tables from scraped data as in-memory objects.

    This is the main entry point for extracting structured tables from
    mytischtennis.de profile data without writing to CSV files.

    Args:
        data: Main response data from fetch_data() or fetch_own_community()
        remaining: Optional remaining text containing deferred TTR history data
        backend: Output format - "polars", "pandas", or "pyarrow"

    Returns:
        Dictionary mapping table names to DataFrame/Table objects.
        Missing tables are omitted from the result (not returned as empty).

        Table names and return types by backend:
        - "club_info": Single-row table with club information
        - "ttr_rankings": TTR rankings within the club
        - "league_table": League standings
        - "ttr_history_events": TTR history event summaries
        - "ttr_history_matches": Individual match details from TTR history

    Raises:
        ValueError: If an unsupported backend is specified
        ImportError: If the required backend library is not installed

    Example:
        >>> # Use environment variables or secure vault for credentials
        >>> scraper = MyTischtennisScraper(username, password)
        >>> scraper.login()
        >>> data, remaining = scraper.fetch_own_community()
        >>> tables = extract_flat_tables(data, remaining, backend="polars")
        >>> print(tables["ttr_rankings"].head())
    """
    if backend not in ("polars", "pandas", "pyarrow"):
        raise ValueError(f"Unsupported backend: {backend!r}. Use 'polars', 'pandas', or 'pyarrow'")

    result: dict[str, Any] = {}

    # Select converter based on backend
    if backend == "polars":
        converter = _to_polars_df
    elif backend == "pandas":
        converter = _to_pandas_df
    else:  # pyarrow
        converter = _to_pyarrow_table

    # Extract club info
    club_info_records = _extract_club_info_records(data)
    if club_info_records is not None:
        result["club_info"] = converter(club_info_records, CLUB_INFO_FIELDS + ["extracted_at"])

    # Extract TTR rankings
    ttr_rankings_records = _extract_ttr_rankings_records(data)
    if ttr_rankings_records is not None:
        result["ttr_rankings"] = converter(ttr_rankings_records, TTR_RANKING_FIELDS)

    # Extract league table
    league_table_records = _extract_league_table_records(data)
    if league_table_records is not None:
        result["league_table"] = converter(league_table_records, LEAGUE_TABLE_FIELDS)

    # Extract TTR history from remaining data
    if remaining:
        history = _extract_ttr_history_from_remaining(remaining)
        if history:
            # Events table
            events_records = _extract_ttr_history_events_records(history)
            if events_records is not None:
                result["ttr_history_events"] = converter(events_records, TTR_HISTORY_EVENTS_FIELDS)

            # Matches table
            matches_records = _extract_ttr_history_matches_records(history)
            if matches_records is not None:
                result["ttr_history_matches"] = converter(matches_records, TTR_HISTORY_MATCHES_FIELDS)

    return result
