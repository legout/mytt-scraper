"""Tests for the query executor."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src directory to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

import polars as pl

from mytt_scraper.utils.query_executor import (
    PolarsQueryExecutor,
    QueryExecutorError,
    ValidationError,
    create_executor,
)
from mytt_scraper.utils.query_model import (
    AggFunc,
    Aggregation,
    Filter,
    FilterOp,
    GroupBy,
    Query,
    Sort,
    SortDirection,
)


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pl.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "club": ["Berlin", "Munich", "Berlin", "Hamburg", "Munich"],
        "ttr": [1500, 1600, 1550, 1700, 1450],
        "position": [1, 2, 3, 1, 2],
    })


@pytest.fixture
def executor():
    """Create a query executor for testing."""
    return PolarsQueryExecutor(validate=False)


class TestPolarsQueryExecutor:
    """Tests for PolarsQueryExecutor."""

    def test_executor_creation(self):
        """Should create an executor."""
        ex = PolarsQueryExecutor()
        assert ex.validate is True

    def test_executor_creation_no_validation(self):
        """Should create an executor without validation."""
        ex = PolarsQueryExecutor(validate=False)
        assert ex.validate is False

    def test_empty_query(self, executor, sample_df):
        """Empty query should return unchanged DataFrame."""
        query = Query()
        result = executor.execute(sample_df, query)
        assert len(result) == len(sample_df)
        assert list(result.columns) == list(sample_df.columns)

    def test_filter_eq(self, executor, sample_df):
        """Should filter with EQ operator."""
        query = Query(filters=[Filter("club", FilterOp.EQ, "Berlin")])
        result = executor.execute(sample_df, query)
        assert len(result) == 2
        assert set(result["name"].to_list()) == {"Alice", "Charlie"}

    def test_filter_ne(self, executor, sample_df):
        """Should filter with NE operator."""
        query = Query(filters=[Filter("club", FilterOp.NE, "Berlin")])
        result = executor.execute(sample_df, query)
        assert len(result) == 3

    def test_filter_gt(self, executor, sample_df):
        """Should filter with GT operator."""
        query = Query(filters=[Filter("ttr", FilterOp.GT, 1550)])
        result = executor.execute(sample_df, query)
        assert len(result) == 2  # Bob (1600), Diana (1700)
        assert set(result["name"].to_list()) == {"Bob", "Diana"}

    def test_filter_gte(self, executor, sample_df):
        """Should filter with GTE operator."""
        query = Query(filters=[Filter("ttr", FilterOp.GTE, 1550)])
        result = executor.execute(sample_df, query)
        assert len(result) == 3  # Charlie (1550), Bob (1600), Diana (1700)

    def test_filter_lt(self, executor, sample_df):
        """Should filter with LT operator."""
        query = Query(filters=[Filter("ttr", FilterOp.LT, 1500)])
        result = executor.execute(sample_df, query)
        assert len(result) == 1  # Eve (1450)
        assert result["name"][0] == "Eve"

    def test_filter_lte(self, executor, sample_df):
        """Should filter with LTE operator."""
        query = Query(filters=[Filter("ttr", FilterOp.LTE, 1500)])
        result = executor.execute(sample_df, query)
        assert len(result) == 2  # Alice (1500), Eve (1450)

    def test_filter_contains(self, executor, sample_df):
        """Should filter with CONTAINS operator."""
        query = Query(filters=[Filter("name", FilterOp.CONTAINS, "li")])
        result = executor.execute(sample_df, query)
        assert len(result) == 2  # Alice, Charlie

    def test_filter_starts_with(self, executor, sample_df):
        """Should filter with STARTS_WITH operator."""
        query = Query(filters=[Filter("name", FilterOp.STARTS_WITH, "A")])
        result = executor.execute(sample_df, query)
        assert len(result) == 1
        assert result["name"][0] == "Alice"

    def test_filter_ends_with(self, executor, sample_df):
        """Should filter with ENDS_WITH operator."""
        query = Query(filters=[Filter("name", FilterOp.ENDS_WITH, "e")])
        result = executor.execute(sample_df, query)
        assert len(result) == 3  # Alice, Charlie, Eve

    def test_filter_in(self, executor, sample_df):
        """Should filter with IN operator."""
        query = Query(filters=[Filter("club", FilterOp.IN, ["Berlin", "Hamburg"])])
        result = executor.execute(sample_df, query)
        assert len(result) == 3

    def test_filter_is_null(self, executor):
        """Should filter with IS_NULL operator."""
        df = pl.DataFrame({
            "name": ["Alice", "Bob", None],
            "ttr": [1500, None, 1600],
        })
        query = Query(filters=[Filter("ttr", FilterOp.IS_NULL)])
        result = executor.execute(df, query)
        assert len(result) == 1
        assert result["name"][0] == "Bob"

    def test_filter_is_not_null(self, executor):
        """Should filter with IS_NOT_NULL operator."""
        df = pl.DataFrame({
            "name": ["Alice", "Bob", None],
            "ttr": [1500, None, 1600],
        })
        query = Query(filters=[Filter("ttr", FilterOp.IS_NOT_NULL)])
        result = executor.execute(df, query)
        assert len(result) == 2

    def test_multiple_filters(self, executor, sample_df):
        """Multiple filters should be ANDed together."""
        query = Query(filters=[
            Filter("club", FilterOp.EQ, "Berlin"),
            Filter("ttr", FilterOp.GT, 1520),
        ])
        result = executor.execute(sample_df, query)
        assert len(result) == 1  # Only Charlie (1550)

    def test_sort_asc(self, executor, sample_df):
        """Should sort ascending."""
        query = Query(sort=[Sort("ttr", SortDirection.ASC)])
        result = executor.execute(sample_df, query)
        ttr_values = result["ttr"].to_list()
        assert ttr_values == sorted(ttr_values)

    def test_sort_desc(self, executor, sample_df):
        """Should sort descending."""
        query = Query(sort=[Sort("ttr", SortDirection.DESC)])
        result = executor.execute(sample_df, query)
        ttr_values = result["ttr"].to_list()
        assert ttr_values == sorted(ttr_values, reverse=True)

    def test_sort_multiple(self, executor, sample_df):
        """Should apply multiple sorts in order."""
        query = Query(sort=[
            Sort("club", SortDirection.ASC),
            Sort("ttr", SortDirection.DESC),
        ])
        result = executor.execute(sample_df, query)
        # Berlin: Charlie (1550), Alice (1500)
        # Hamburg: Diana (1700)
        # Munich: Bob (1600), Eve (1450)
        assert result["name"].to_list() == ["Charlie", "Alice", "Diana", "Bob", "Eve"]

    def test_limit(self, executor, sample_df):
        """Should limit results."""
        query = Query(limit=3)
        result = executor.execute(sample_df, query)
        assert len(result) == 3

    def test_offset(self, executor, sample_df):
        """Should offset results."""
        query = Query(offset=2)
        result = executor.execute(sample_df, query)
        assert len(result) == 3  # 5 - 2 = 3

    def test_limit_and_offset(self, executor, sample_df):
        """Should apply limit and offset together."""
        query = Query(limit=2, offset=1)
        result = executor.execute(sample_df, query)
        assert len(result) == 2

    def test_groupby_count(self, executor, sample_df):
        """Should groupby and count."""
        query = Query(groupby=GroupBy(
            ["club"],
            [Aggregation("*", AggFunc.COUNT, alias="count")],
        ))
        result = executor.execute(sample_df, query)
        assert len(result) == 3  # 3 unique clubs
        # Check that count column exists
        assert "count" in result.columns

    def test_groupby_avg(self, executor, sample_df):
        """Should groupby and calculate average."""
        query = Query(groupby=GroupBy(
            ["club"],
            [Aggregation("ttr", AggFunc.AVG, alias="avg_ttr")],
        ))
        result = executor.execute(sample_df, query)
        berlin_row = result.filter(pl.col("club") == "Berlin")
        # (1500 + 1550) / 2 = 1525
        assert berlin_row["avg_ttr"][0] == 1525.0

    def test_groupby_sum(self, executor, sample_df):
        """Should groupby and sum."""
        query = Query(groupby=GroupBy(
            ["club"],
            [Aggregation("ttr", AggFunc.SUM, alias="sum_ttr")],
        ))
        result = executor.execute(sample_df, query)
        berlin_row = result.filter(pl.col("club") == "Berlin")
        assert berlin_row["sum_ttr"][0] == 3050  # 1500 + 1550

    def test_groupby_min_max(self, executor, sample_df):
        """Should groupby and get min/max."""
        query = Query(groupby=GroupBy(
            ["club"],
            [
                Aggregation("ttr", AggFunc.MIN, alias="min_ttr"),
                Aggregation("ttr", AggFunc.MAX, alias="max_ttr"),
            ],
        ))
        result = executor.execute(sample_df, query)
        berlin_row = result.filter(pl.col("club") == "Berlin")
        assert berlin_row["min_ttr"][0] == 1500
        assert berlin_row["max_ttr"][0] == 1550

    def test_groupby_multiple_columns(self, executor, sample_df):
        """Should groupby multiple columns."""
        query = Query(groupby=GroupBy(
            ["club", "position"],
            [Aggregation("*", AggFunc.COUNT, alias="count")],
        ))
        result = executor.execute(sample_df, query)
        # Berlin: positions 1 (Alice) and 3 (Charlie) = 2 groups
        # Hamburg: position 1 (Diana) = 1 group
        # Munich: position 2 (Bob, Eve) = 1 group (duplicate, aggregated)
        # Total: 4 groups
        assert len(result) == 4

    def test_complex_query(self, executor, sample_df):
        """Should handle complex query with all operations."""
        query = Query(
            filters=[Filter("ttr", FilterOp.GTE, 1500)],
            groupby=GroupBy(
                ["club"],
                [
                    Aggregation("ttr", AggFunc.AVG, alias="avg_ttr"),
                    Aggregation("*", AggFunc.COUNT, alias="count"),
                ],
            ),
            sort=[Sort("avg_ttr", SortDirection.DESC)],
            limit=2,
        )
        result = executor.execute(sample_df, query)
        # Should have filtered Eve (1450), grouped by club, sorted by avg_ttr desc, limited to 2
        assert len(result) == 2


class TestPolarsQueryExecutorValidation:
    """Tests for query validation in executor."""

    def test_validation_enabled_raises(self, sample_df):
        """Should raise ValidationError when validation fails."""
        executor = PolarsQueryExecutor(validate=True)
        query = Query(filters=[Filter("nonexistent", FilterOp.EQ, "value")])
        with pytest.raises(ValidationError):
            executor.execute(sample_df, query)

    def test_validation_disabled_succeeds(self, sample_df):
        """Should not raise when validation is disabled."""
        executor = PolarsQueryExecutor(validate=False)
        query = Query(filters=[Filter("nonexistent", FilterOp.EQ, "value")])
        # Will fail at execution time, not validation
        with pytest.raises(Exception):
            executor.execute(sample_df, query)


class TestPolarsQueryExecutorCsv:
    """Tests for CSV execution."""

    def test_execute_csv(self, tmp_path):
        """Should execute query against CSV file."""
        # Create a test CSV
        csv_path = tmp_path / "test.csv"
        df = pl.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "ttr": [1500, 1600, 1550],
        })
        df.write_csv(csv_path)

        executor = PolarsQueryExecutor(validate=False)
        query = Query(
            filters=[Filter("ttr", FilterOp.GT, 1520)],
            sort=[Sort("name")],
        )

        result = executor.execute_csv(str(csv_path), query)
        assert len(result) == 2
        assert set(result["name"].to_list()) == {"Bob", "Charlie"}

    def test_execute_csv_not_found(self, tmp_path):
        """Should raise error for non-existent CSV."""
        executor = PolarsQueryExecutor(validate=False)
        query = Query()

        with pytest.raises(QueryExecutorError):
            executor.execute_csv(str(tmp_path / "nonexistent.csv"), query)


class TestCreateExecutor:
    """Tests for create_executor factory function."""

    def test_create_polars_executor(self):
        """Should create a PolarsQueryExecutor."""
        executor = create_executor("polars")
        assert isinstance(executor, PolarsQueryExecutor)

    def test_create_polars_executor_with_kwargs(self):
        """Should pass kwargs to executor constructor."""
        executor = create_executor("polars", validate=False)
        assert executor.validate is False

    def test_create_invalid_backend(self):
        """Should raise error for invalid backend."""
        with pytest.raises(ValueError, match="Unsupported backend"):
            create_executor("invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
