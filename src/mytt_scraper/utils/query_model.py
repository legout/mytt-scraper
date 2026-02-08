"""Query model for table viewer filters, sort, and aggregation operations.

This module provides a backend-agnostic query model that can be executed
via different backends (Polars first, DuckDB optionally later).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Literal


class FilterOp(Enum):
    """Filter operators for column comparisons."""

    EQ = auto()  # Equal
    NE = auto()  # Not equal
    GT = auto()  # Greater than
    GTE = auto()  # Greater than or equal
    LT = auto()  # Less than
    LTE = auto()  # Less than or equal
    CONTAINS = auto()  # String contains
    STARTS_WITH = auto()  # String starts with
    ENDS_WITH = auto()  # String ends with
    IN = auto()  # In list
    IS_NULL = auto()  # Is null
    IS_NOT_NULL = auto()  # Is not null


class SortDirection(Enum):
    """Sort direction for ordering results."""

    ASC = auto()
    DESC = auto()


class AggFunc(Enum):
    """Aggregation functions for groupby operations."""

    COUNT = auto()
    SUM = auto()
    AVG = auto()
    MEAN = auto()
    MIN = auto()
    MAX = auto()
    FIRST = auto()
    LAST = auto()


@dataclass(frozen=True)
class Filter:
    """A filter condition on a column.

    Attributes:
        column: Column name to filter on
        op: Filter operator
        value: Value to compare against (None for IS_NULL/IS_NOT_NULL)

    Examples:
        >>> Filter("ttr", FilterOp.GT, 1500)
        >>> Filter("name", FilterOp.CONTAINS, "Smith")
        >>> Filter("club", FilterOp.IS_NULL)  # value is optional for null checks
    """

    column: str
    op: FilterOp
    value: Any = None

    def __post_init__(self) -> None:
        """Validate filter after creation."""
        # IS_NULL and IS_NOT_NULL don't require a value
        if self.op in (FilterOp.IS_NULL, FilterOp.IS_NOT_NULL):
            object.__setattr__(self, "value", None)


@dataclass(frozen=True)
class Sort:
    """A sort specification for ordering results.

    Attributes:
        column: Column name to sort by
        direction: Sort direction (ASC or DESC)

    Examples:
        >>> Sort("ttr", SortDirection.DESC)
        >>> Sort("name")  # Defaults to ASC
    """

    column: str
    direction: SortDirection = SortDirection.ASC


@dataclass(frozen=True)
class Aggregation:
    """An aggregation specification for groupby operations.

    Attributes:
        column: Column to aggregate (can be "*" for COUNT)
        func: Aggregation function
        alias: Optional output column name (defaults to "{column}_{func}")

    Examples:
        >>> Aggregation("ttr", AggFunc.AVG)
        >>> Aggregation("ttr", AggFunc.AVG, alias="avg_ttr")
        >>> Aggregation("*", AggFunc.COUNT, alias="total")
    """

    column: str
    func: AggFunc
    alias: str | None = None

    def __post_init__(self) -> None:
        """Set default alias if not provided."""
        if self.alias is None:
            default_alias = f"{self.column}_{self.func.name.lower()}"
            object.__setattr__(self, "alias", default_alias)


@dataclass(frozen=True)
class GroupBy:
    """A groupby specification with aggregations.

    Attributes:
        columns: List of column names to group by
        aggregations: List of aggregation specifications

    Examples:
        >>> GroupBy(["club"], [Aggregation("ttr", AggFunc.AVG)])
        >>> GroupBy(["club", "position"], [
        ...     Aggregation("ttr", AggFunc.AVG),
        ...     Aggregation("*", AggFunc.COUNT, alias="count")
        ... ])
    """

    columns: list[str]
    aggregations: list[Aggregation]

    def __post_init__(self) -> None:
        """Validate groupby after creation."""
        if not self.columns:
            raise ValueError("GroupBy must have at least one column")
        if not self.aggregations:
            raise ValueError("GroupBy must have at least one aggregation")


@dataclass
class TableSchema:
    """Schema definition for table validation.

    Attributes:
        columns: Dictionary mapping column names to their types

    Examples:
        >>> schema = TableSchema({
        ...     "name": "string",
        ...     "ttr": "int",
        ...     "joined": "datetime"
        ... })
    """

    columns: dict[str, str]

    def validate_column(self, column: str) -> bool:
        """Check if a column exists in the schema.

        Args:
            column: Column name to validate

        Returns:
            True if column exists, False otherwise
        """
        return column in self.columns

    def validate_columns(self, columns: list[str]) -> tuple[bool, list[str]]:
        """Validate multiple columns against the schema.

        Args:
            columns: List of column names to validate

        Returns:
            Tuple of (all_valid, list_of_invalid_columns)
        """
        invalid = [col for col in columns if not self.validate_column(col)]
        return len(invalid) == 0, invalid

    def get_column_type(self, column: str) -> str | None:
        """Get the type of a column.

        Args:
            column: Column name

        Returns:
            Column type string, or None if column doesn't exist
        """
        return self.columns.get(column)


@dataclass
class Query:
    """Complete query specification for table operations.

    This is the main query model that combines filters, sort, and groupby
    operations. It can be validated against a schema and executed by
    different backends.

    Attributes:
        filters: List of filter conditions (ANDed together)
        sort: List of sort specifications (applied in order)
        groupby: Optional groupby with aggregations
        limit: Optional row limit
        offset: Optional row offset for pagination

    Examples:
        >>> # Simple filter and sort
        >>> query = Query(
        ...     filters=[Filter("ttr", FilterOp.GT, 1500)],
        ...     sort=[Sort("name", SortDirection.ASC)]
        ... )
        >>>
        >>> # Groupby with multiple aggregations
        >>> query = Query(
        ...     filters=[Filter("club", FilterOp.EQ, "Berlin")],
        ...     groupby=GroupBy(
        ...         columns=["position"],
        ...         aggregations=[
        ...             Aggregation("ttr", AggFunc.AVG, alias="avg_ttr"),
        ...             Aggregation("*", AggFunc.COUNT, alias="count")
        ...         ]
        ...     )
        ... )
    """

    filters: list[Filter] = field(default_factory=list)
    sort: list[Sort] = field(default_factory=list)
    groupby: GroupBy | None = None
    limit: int | None = None
    offset: int | None = None

    def validate(self, schema: TableSchema) -> tuple[bool, list[str]]:
        """Validate the query against a table schema.

        Args:
            schema: Table schema to validate against

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors: list[str] = []

        # Validate filter columns
        for f in self.filters:
            if not schema.validate_column(f.column):
                errors.append(f"Filter references unknown column: {f.column}")

        # Validate sort columns
        # When groupby is present, sort can reference aggregation aliases
        valid_sort_columns = set(schema.columns.keys())
        if self.groupby:
            # Add aggregation aliases as valid sort columns
            for agg in self.groupby.aggregations:
                valid_sort_columns.add(agg.alias)

        for s in self.sort:
            if s.column not in valid_sort_columns:
                errors.append(f"Sort references unknown column: {s.column}")

        # Validate groupby columns and aggregations
        if self.groupby:
            valid, invalid = schema.validate_columns(self.groupby.columns)
            if not valid:
                for col in invalid:
                    errors.append(f"GroupBy references unknown column: {col}")

            for agg in self.groupby.aggregations:
                # COUNT(*) is special - doesn't reference a column
                if agg.func == AggFunc.COUNT and agg.column == "*":
                    continue
                if not schema.validate_column(agg.column):
                    errors.append(f"Aggregation references unknown column: {agg.column}")

        # Validate limit and offset
        if self.limit is not None and self.limit < 0:
            errors.append(f"Limit must be non-negative, got: {self.limit}")
        if self.offset is not None and self.offset < 0:
            errors.append(f"Offset must be non-negative, got: {self.offset}")

        return len(errors) == 0, errors

    def is_empty(self) -> bool:
        """Check if the query has any operations defined.

        Returns:
            True if no filters, sort, groupby, limit, or offset are set
        """
        return (
            len(self.filters) == 0
            and len(self.sort) == 0
            and self.groupby is None
            and self.limit is None
            and self.offset is None
        )


# Type alias for backend types
Backend = Literal["polars", "duckdb"]
