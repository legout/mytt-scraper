"""Tests for the query model data structures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src directory to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from mytt_scraper.utils.query_model import (
    AggFunc,
    Aggregation,
    Filter,
    FilterOp,
    GroupBy,
    Query,
    Sort,
    SortDirection,
    TableSchema,
)


class TestFilter:
    """Tests for Filter dataclass."""

    def test_filter_creation(self):
        """Should create a filter with column, op, and value."""
        f = Filter("ttr", FilterOp.GT, 1500)
        assert f.column == "ttr"
        assert f.op == FilterOp.GT
        assert f.value == 1500

    def test_filter_equality(self):
        """Filters with same values should be equal."""
        f1 = Filter("name", FilterOp.EQ, "Alice")
        f2 = Filter("name", FilterOp.EQ, "Alice")
        assert f1 == f2

    def test_filter_hashable(self):
        """Filters should be hashable (frozen dataclass)."""
        f = Filter("ttr", FilterOp.GT, 1500)
        # Should not raise
        hash(f)

    def test_filter_is_null_no_value(self):
        """IS_NULL filter should not require a value."""
        f = Filter("name", FilterOp.IS_NULL)
        assert f.column == "name"
        assert f.op == FilterOp.IS_NULL
        assert f.value is None

    def test_filter_is_not_null_no_value(self):
        """IS_NOT_NULL filter should not require a value."""
        f = Filter("name", FilterOp.IS_NOT_NULL)
        assert f.column == "name"
        assert f.op == FilterOp.IS_NOT_NULL
        assert f.value is None

    def test_filter_all_operators(self):
        """All filter operators should be usable."""
        operators = [
            FilterOp.EQ,
            FilterOp.NE,
            FilterOp.GT,
            FilterOp.GTE,
            FilterOp.LT,
            FilterOp.LTE,
            FilterOp.CONTAINS,
            FilterOp.STARTS_WITH,
            FilterOp.ENDS_WITH,
            FilterOp.IN,
            FilterOp.IS_NULL,
            FilterOp.IS_NOT_NULL,
        ]
        for op in operators:
            if op in (FilterOp.IS_NULL, FilterOp.IS_NOT_NULL):
                f = Filter("col", op)
            elif op == FilterOp.IN:
                f = Filter("col", op, [1, 2, 3])
            else:
                f = Filter("col", op, "value")
            assert f.op == op


class TestSort:
    """Tests for Sort dataclass."""

    def test_sort_creation(self):
        """Should create a sort with column and direction."""
        s = Sort("ttr", SortDirection.DESC)
        assert s.column == "ttr"
        assert s.direction == SortDirection.DESC

    def test_sort_default_direction(self):
        """Sort should default to ASC direction."""
        s = Sort("name")
        assert s.direction == SortDirection.ASC

    def test_sort_hashable(self):
        """Sorts should be hashable (frozen dataclass)."""
        s = Sort("ttr", SortDirection.DESC)
        hash(s)


class TestAggregation:
    """Tests for Aggregation dataclass."""

    def test_aggregation_creation(self):
        """Should create an aggregation with column and function."""
        a = Aggregation("ttr", AggFunc.AVG)
        assert a.column == "ttr"
        assert a.func == AggFunc.AVG
        assert a.alias == "ttr_avg"  # Auto-generated

    def test_aggregation_with_alias(self):
        """Should accept a custom alias."""
        a = Aggregation("ttr", AggFunc.AVG, alias="average_ttr")
        assert a.alias == "average_ttr"

    def test_aggregation_count_star(self):
        """COUNT(*) should be supported."""
        a = Aggregation("*", AggFunc.COUNT, alias="total")
        assert a.column == "*"
        assert a.func == AggFunc.COUNT
        assert a.alias == "total"

    def test_aggregation_all_functions(self):
        """All aggregation functions should be usable."""
        funcs = [
            AggFunc.COUNT,
            AggFunc.SUM,
            AggFunc.AVG,
            AggFunc.MEAN,
            AggFunc.MIN,
            AggFunc.MAX,
            AggFunc.FIRST,
            AggFunc.LAST,
        ]
        for func in funcs:
            a = Aggregation("col", func)
            assert a.func == func

    def test_aggregation_hashable(self):
        """Aggregations should be hashable (frozen dataclass)."""
        a = Aggregation("ttr", AggFunc.AVG)
        hash(a)


class TestGroupBy:
    """Tests for GroupBy dataclass."""

    def test_groupby_creation(self):
        """Should create a groupby with columns and aggregations."""
        agg = Aggregation("ttr", AggFunc.AVG)
        gb = GroupBy(["club"], [agg])
        assert gb.columns == ["club"]
        assert len(gb.aggregations) == 1

    def test_groupby_multiple_columns(self):
        """Should support multiple groupby columns."""
        agg = Aggregation("ttr", AggFunc.AVG)
        gb = GroupBy(["club", "position"], [agg])
        assert gb.columns == ["club", "position"]

    def test_groupby_multiple_aggregations(self):
        """Should support multiple aggregations."""
        aggs = [
            Aggregation("ttr", AggFunc.AVG),
            Aggregation("*", AggFunc.COUNT, alias="count"),
        ]
        gb = GroupBy(["club"], aggs)
        assert len(gb.aggregations) == 2

    def test_groupby_empty_columns_raises(self):
        """Should raise error when no columns provided."""
        agg = Aggregation("ttr", AggFunc.AVG)
        with pytest.raises(ValueError, match="at least one column"):
            GroupBy([], [agg])

    def test_groupby_empty_aggregations_raises(self):
        """Should raise error when no aggregations provided."""
        with pytest.raises(ValueError, match="at least one aggregation"):
            GroupBy(["club"], [])


class TestTableSchema:
    """Tests for TableSchema."""

    @pytest.fixture
    def sample_schema(self):
        """Create a sample schema for testing."""
        return TableSchema({
            "name": "string",
            "ttr": "int",
            "club": "string",
            "joined": "datetime",
        })

    def test_schema_creation(self):
        """Should create a schema with columns."""
        schema = TableSchema({"col1": "string", "col2": "int"})
        assert "col1" in schema.columns
        assert "col2" in schema.columns

    def test_validate_column_exists(self, sample_schema):
        """Should return True for existing columns."""
        assert sample_schema.validate_column("name") is True
        assert sample_schema.validate_column("ttr") is True

    def test_validate_column_missing(self, sample_schema):
        """Should return False for non-existent columns."""
        assert sample_schema.validate_column("nonexistent") is False

    def test_validate_columns_all_valid(self, sample_schema):
        """Should return True when all columns exist."""
        valid, invalid = sample_schema.validate_columns(["name", "ttr"])
        assert valid is True
        assert invalid == []

    def test_validate_columns_some_invalid(self, sample_schema):
        """Should return False and list invalid columns."""
        valid, invalid = sample_schema.validate_columns(["name", "missing", "ttr", "also_missing"])
        assert valid is False
        assert "missing" in invalid
        assert "also_missing" in invalid
        assert "name" not in invalid

    def test_get_column_type(self, sample_schema):
        """Should return the type of a column."""
        assert sample_schema.get_column_type("name") == "string"
        assert sample_schema.get_column_type("ttr") == "int"

    def test_get_column_type_missing(self, sample_schema):
        """Should return None for non-existent columns."""
        assert sample_schema.get_column_type("missing") is None


class TestQuery:
    """Tests for Query dataclass."""

    @pytest.fixture
    def sample_schema(self):
        """Create a sample schema for testing."""
        return TableSchema({
            "name": "string",
            "ttr": "int",
            "club": "string",
            "position": "string",
        })

    def test_empty_query(self):
        """Should create an empty query."""
        q = Query()
        assert q.filters == []
        assert q.sort == []
        assert q.groupby is None
        assert q.limit is None
        assert q.offset is None

    def test_query_with_filters(self):
        """Should create a query with filters."""
        q = Query(
            filters=[
                Filter("ttr", FilterOp.GT, 1500),
                Filter("club", FilterOp.EQ, "Berlin"),
            ]
        )
        assert len(q.filters) == 2

    def test_query_with_sort(self):
        """Should create a query with sort."""
        q = Query(
            sort=[
                Sort("ttr", SortDirection.DESC),
                Sort("name"),
            ]
        )
        assert len(q.sort) == 2

    def test_query_with_groupby(self):
        """Should create a query with groupby."""
        gb = GroupBy(
            ["club"],
            [Aggregation("ttr", AggFunc.AVG)],
        )
        q = Query(groupby=gb)
        assert q.groupby is not None

    def test_query_with_limit_offset(self):
        """Should create a query with limit and offset."""
        q = Query(limit=10, offset=5)
        assert q.limit == 10
        assert q.offset == 5

    def test_is_empty_true(self):
        """Should return True for empty query."""
        q = Query()
        assert q.is_empty() is True

    def test_is_empty_false_with_filters(self):
        """Should return False when filters present."""
        q = Query(filters=[Filter("ttr", FilterOp.GT, 1500)])
        assert q.is_empty() is False

    def test_is_empty_false_with_sort(self):
        """Should return False when sort present."""
        q = Query(sort=[Sort("name")])
        assert q.is_empty() is False

    def test_is_empty_false_with_groupby(self):
        """Should return False when groupby present."""
        gb = GroupBy(["club"], [Aggregation("ttr", AggFunc.AVG)])
        q = Query(groupby=gb)
        assert q.is_empty() is False

    def test_is_empty_false_with_limit(self):
        """Should return False when limit present."""
        q = Query(limit=10)
        assert q.is_empty() is False

    def test_is_empty_false_with_offset(self):
        """Should return False when offset present."""
        q = Query(offset=5)
        assert q.is_empty() is False

    def test_validate_valid_query(self, sample_schema):
        """Should validate a correct query."""
        q = Query(
            filters=[Filter("ttr", FilterOp.GT, 1500)],
            sort=[Sort("name")],
        )
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is True
        assert errors == []

    def test_validate_invalid_filter_column(self, sample_schema):
        """Should detect invalid filter column."""
        q = Query(filters=[Filter("invalid", FilterOp.EQ, "value")])
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is False
        assert any("invalid" in e and "Filter" in e for e in errors)

    def test_validate_invalid_sort_column(self, sample_schema):
        """Should detect invalid sort column."""
        q = Query(sort=[Sort("invalid")])
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is False
        assert any("invalid" in e and "Sort" in e for e in errors)

    def test_validate_invalid_groupby_column(self, sample_schema):
        """Should detect invalid groupby column."""
        gb = GroupBy(["invalid"], [Aggregation("ttr", AggFunc.AVG)])
        q = Query(groupby=gb)
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is False
        assert any("invalid" in e and "GroupBy" in e for e in errors)

    def test_validate_invalid_aggregation_column(self, sample_schema):
        """Should detect invalid aggregation column."""
        gb = GroupBy(["club"], [Aggregation("invalid", AggFunc.AVG)])
        q = Query(groupby=gb)
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is False
        assert any("invalid" in e and "Aggregation" in e for e in errors)

    def test_validate_count_star_valid(self, sample_schema):
        """COUNT(*) should be valid without column check."""
        gb = GroupBy(["club"], [Aggregation("*", AggFunc.COUNT, alias="total")])
        q = Query(groupby=gb)
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is True

    def test_validate_negative_limit(self, sample_schema):
        """Should detect negative limit."""
        q = Query(limit=-1)
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is False
        assert any("Limit" in e for e in errors)

    def test_validate_negative_offset(self, sample_schema):
        """Should detect negative offset."""
        q = Query(offset=-5)
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is False
        assert any("Offset" in e for e in errors)

    def test_validate_multiple_errors(self, sample_schema):
        """Should collect all validation errors."""
        gb = GroupBy(["invalid_col"], [Aggregation("another_invalid", AggFunc.AVG)])
        q = Query(
            filters=[Filter("bad_filter", FilterOp.EQ, "x")],
            sort=[Sort("bad_sort")],
            groupby=gb,
        )
        is_valid, errors = q.validate(sample_schema)
        assert is_valid is False
        assert len(errors) == 4  # filter, sort, groupby col, agg col


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
