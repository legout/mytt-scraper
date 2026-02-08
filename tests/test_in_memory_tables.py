"""Tests for in-memory flat table extraction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Add src directory to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from mytt_scraper.config import (
    CLUB_INFO_FIELDS,
    LEAGUE_TABLE_FIELDS,
    TTR_HISTORY_EVENTS_FIELDS,
    TTR_HISTORY_MATCHES_FIELDS,
    TTR_RANKING_FIELDS,
)
from mytt_scraper.utils.in_memory_tables import extract_flat_tables


# Fixture path
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "community_response.json"


@pytest.fixture
def fixture_data():
    """Load the community response fixture data.

    Fixture format:
    - Line 0: main JSON data (no prefix)
    - Line 1: empty
    - Line 2: data:{...} with deferred TTR history
    """
    with open(FIXTURE_PATH, "r") as f:
        content = f.read()

    lines = content.strip().split("\n")

    # Line 0 is the main data (no prefix)
    main_data = json.loads(lines[0])

    # Look for the deferred data line (starts with data:)
    remaining = None
    for line in lines[1:]:
        if line.startswith("data:"):
            remaining = line
            break

    return main_data, remaining


@pytest.fixture
def fixture_data_no_remaining():
    """Load fixture data without remaining (deferred) data."""
    with open(FIXTURE_PATH, "r") as f:
        content = f.read()

    lines = content.strip().split("\n")
    main_data = json.loads(lines[0])  # Line 0 has no prefix

    return main_data


class TestExtractFlatTablesPyArrow:
    """Tests for extract_flat_tables with pyarrow backend."""

    def test_returns_dict(self, fixture_data):
        """Should return a dictionary."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")
        assert isinstance(result, dict)

    def test_returns_expected_tables(self, fixture_data):
        """Should return expected table names."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        expected_tables = [
            "club_info",
            "ttr_rankings",
            "league_table",
            "ttr_history_events",
            "ttr_history_matches",
        ]
        for table_name in expected_tables:
            assert table_name in result, f"Missing table: {table_name}"

    def test_club_info_non_empty(self, fixture_data):
        """club_info should be non-empty."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["club_info"]
        assert table.num_rows > 0, "club_info should have rows"

    def test_club_info_columns(self, fixture_data):
        """club_info should have expected columns."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["club_info"]
        column_names = table.column_names
        expected = CLUB_INFO_FIELDS + ["extracted_at"]

        for col in expected:
            assert col in column_names, f"Missing column: {col}"

    def test_ttr_rankings_non_empty(self, fixture_data):
        """ttr_rankings should be non-empty."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["ttr_rankings"]
        assert table.num_rows > 0, "ttr_rankings should have rows"

    def test_ttr_rankings_columns(self, fixture_data):
        """ttr_rankings should have expected columns."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["ttr_rankings"]
        column_names = table.column_names

        # Check that expected columns are present (some may not be in fixture)
        for col in TTR_RANKING_FIELDS:
            assert col in column_names, f"Missing column: {col}"

    def test_league_table_non_empty(self, fixture_data):
        """league_table should be non-empty."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["league_table"]
        assert table.num_rows > 0, "league_table should have rows"

    def test_league_table_columns(self, fixture_data):
        """league_table should have expected columns."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["league_table"]
        column_names = table.column_names

        for col in LEAGUE_TABLE_FIELDS:
            assert col in column_names, f"Missing column: {col}"

    def test_ttr_history_events_non_empty(self, fixture_data):
        """ttr_history_events should be non-empty."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["ttr_history_events"]
        assert table.num_rows > 0, "ttr_history_events should have rows"

    def test_ttr_history_events_columns(self, fixture_data):
        """ttr_history_events should have expected columns."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["ttr_history_events"]
        column_names = table.column_names

        for col in TTR_HISTORY_EVENTS_FIELDS:
            assert col in column_names, f"Missing column: {col}"

    def test_ttr_history_matches_non_empty(self, fixture_data):
        """ttr_history_matches should be non-empty."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["ttr_history_matches"]
        assert table.num_rows > 0, "ttr_history_matches should have rows"

    def test_ttr_history_matches_columns(self, fixture_data):
        """ttr_history_matches should have expected columns."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["ttr_history_matches"]
        column_names = table.column_names

        # Check core columns that should always be present
        core_columns = [
            "event_id",
            "event_name",
            "match_number",
            "own_person_name",
            "other_person_name",
        ]
        for col in core_columns:
            assert col in column_names, f"Missing core column: {col}"

        # Check that columns from config are present when data exists
        present_config_columns = [c for c in TTR_HISTORY_MATCHES_FIELDS if c in column_names]
        assert len(present_config_columns) >= 5, "Should have at least 5 config columns"

    def test_column_order_club_info(self, fixture_data):
        """club_info columns should be in expected order."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pyarrow")

        table = result["club_info"]
        column_names = table.column_names
        expected = CLUB_INFO_FIELDS + ["extracted_at"]

        # Check that existing columns are in expected order
        existing_expected = [c for c in expected if c in column_names]
        actual_existing = [c for c in column_names if c in expected]
        assert actual_existing == existing_expected, f"Column order mismatch"


class TestExtractFlatTablesPolars:
    """Tests for extract_flat_tables with polars backend."""

    def test_returns_polars_dataframes(self, fixture_data):
        """Should return polars DataFrames."""
        import polars as pl

        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="polars")

        for table_name, table in result.items():
            assert isinstance(
                table, pl.DataFrame
            ), f"{table_name} should be a polars DataFrame"

    def test_expected_tables_present(self, fixture_data):
        """All expected tables should be present."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="polars")

        expected_tables = [
            "club_info",
            "ttr_rankings",
            "league_table",
            "ttr_history_events",
            "ttr_history_matches",
        ]
        for table_name in expected_tables:
            assert table_name in result


class TestExtractFlatTablesPandas:
    """Tests for extract_flat_tables with pandas backend."""

    def test_returns_pandas_dataframes(self, fixture_data):
        """Should return pandas DataFrames."""
        import pandas as pd

        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pandas")

        for table_name, table in result.items():
            assert isinstance(
                table, pd.DataFrame
            ), f"{table_name} should be a pandas DataFrame"

    def test_expected_tables_present(self, fixture_data):
        """All expected tables should be present."""
        data, remaining = fixture_data
        result = extract_flat_tables(data, remaining, backend="pandas")

        expected_tables = [
            "club_info",
            "ttr_rankings",
            "league_table",
            "ttr_history_events",
            "ttr_history_matches",
        ]
        for table_name in expected_tables:
            assert table_name in result


class TestMissingTableBehavior:
    """Tests for missing table behavior (when data is not present)."""

    def test_no_remaining_data_omits_history_tables(self, fixture_data_no_remaining):
        """When remaining is None, history tables should be omitted."""
        data = fixture_data_no_remaining
        result = extract_flat_tables(data, remaining=None, backend="pyarrow")

        # Core tables should still be present
        assert "club_info" in result
        assert "ttr_rankings" in result
        assert "league_table" in result

        # History tables should be omitted
        assert "ttr_history_events" not in result
        assert "ttr_history_matches" not in result

    def test_missing_data_returns_empty_or_omitted(self):
        """Test with minimal/empty data structure."""
        minimal_data = {"pageContent": {"blockLoaderData": {}}}
        result = extract_flat_tables(minimal_data, backend="pyarrow")

        # All tables should be omitted when no data
        assert "club_info" not in result
        assert "ttr_rankings" not in result
        assert "league_table" not in result


class TestBackendValidation:
    """Tests for backend validation."""

    def test_invalid_backend_raises_error(self, fixture_data):
        """Should raise ValueError for invalid backend."""
        data, remaining = fixture_data

        with pytest.raises(ValueError, match="Unsupported backend"):
            extract_flat_tables(data, remaining, backend="invalid_backend")


class TestDataConsistency:
    """Tests for data consistency across backends."""

    def test_same_row_counts_across_backends(self, fixture_data):
        """All backends should return tables with same row counts."""
        data, remaining = fixture_data

        pyarrow_result = extract_flat_tables(data, remaining, backend="pyarrow")
        polars_result = extract_flat_tables(data, remaining, backend="polars")
        pandas_result = extract_flat_tables(data, remaining, backend="pandas")

        for table_name in pyarrow_result.keys():
            pyarrow_rows = pyarrow_result[table_name].num_rows
            polars_rows = len(polars_result[table_name])
            pandas_rows = len(pandas_result[table_name])

            assert (
                pyarrow_rows == polars_rows == pandas_rows
            ), f"{table_name} row count mismatch"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
