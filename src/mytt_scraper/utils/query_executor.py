"""Query executor for executing Query models against different backends.

Provides executors for Polars (MVP) and DuckDB SQL.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from .query_model import AggFunc, FilterOp, Query, SortDirection

if TYPE_CHECKING:
    import polars as pl


class QueryExecutorError(Exception):
    """Base exception for query execution errors."""

    pass


class ValidationError(QueryExecutorError):
    """Raised when query validation fails."""

    pass


class UnsafeQueryError(ValidationError):
    """Raised when a SQL query is deemed unsafe (non-SELECT)."""

    pass


class PolarsQueryExecutor:
    """Execute Query models against Polars DataFrames.

    This is the primary executor for in-memory tables. It also supports
    scan_csv for disk-backed tables via lazy evaluation.

    Examples:
        >>> import polars as pl
        >>> from mytt_scraper.utils.query_model import Query, Filter, FilterOp, Sort
        >>> from mytt_scraper.utils.query_executor import PolarsQueryExecutor
        >>>
        >>> df = pl.DataFrame({"name": ["Alice", "Bob"], "ttr": [1500, 1600]})
        >>> executor = PolarsQueryExecutor()
        >>> query = Query(
        ...     filters=[Filter("ttr", FilterOp.GT, 1550)],
        ...     sort=[Sort("name")]
        ... )
        >>> result = executor.execute(df, query)
    """

    # Mapping of FilterOp to Polars filter expressions
    _FILTER_OPS: dict[FilterOp, str] = {
        FilterOp.EQ: "eq",
        FilterOp.NE: "ne",
        FilterOp.GT: "gt",
        FilterOp.GTE: "ge",
        FilterOp.LT: "lt",
        FilterOp.LTE: "le",
    }

    # Mapping of AggFunc to Polars aggregation methods
    _AGG_FUNCS: dict[AggFunc, str] = {
        AggFunc.COUNT: "count",
        AggFunc.SUM: "sum",
        AggFunc.AVG: "mean",
        AggFunc.MEAN: "mean",
        AggFunc.MIN: "min",
        AggFunc.MAX: "max",
        AggFunc.FIRST: "first",
        AggFunc.LAST: "last",
    }

    def __init__(self, validate: bool = True) -> None:
        """Initialize the executor.

        Args:
            validate: Whether to validate queries before execution
        """
        self.validate = validate

    def execute(self, df: pl.DataFrame, query: Query) -> pl.DataFrame:
        """Execute a query against a Polars DataFrame.

        Args:
            df: Input DataFrame
            query: Query specification

        Returns:
            Result DataFrame after applying query operations

        Raises:
            ValidationError: If query validation fails and validate=True
            QueryExecutorError: If execution fails
        """
        import polars as pl

        # Validate if enabled
        if self.validate:
            from .query_model import TableSchema

            schema = TableSchema({col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)})
            is_valid, errors = query.validate(schema)
            if not is_valid:
                raise ValidationError(f"Query validation failed: {'; '.join(errors)}")

        # Start with lazy frame for optimization
        lazy_df = df.lazy()

        # Apply filters
        for f in query.filters:
            lazy_df = self._apply_filter(lazy_df, f)

        # Apply groupby if present
        if query.groupby:
            lazy_df = self._apply_groupby(lazy_df, query.groupby)

        # Apply sort (after groupby if present, before limit)
        if query.sort:
            lazy_df = self._apply_sorts(lazy_df, query.sort)

        # Apply offset
        if query.offset:
            lazy_df = lazy_df.slice(query.offset)

        # Apply limit
        if query.limit is not None:
            lazy_df = lazy_df.limit(query.limit)

        # Execute and return
        try:
            return lazy_df.collect()
        except Exception as e:
            raise QueryExecutorError(f"Query execution failed: {e}") from e

    def _apply_filter(self, lazy_df: pl.LazyFrame, filter_spec: Any) -> pl.LazyFrame:
        """Apply a filter to a lazy DataFrame.

        Args:
            lazy_df: Lazy DataFrame
            filter_spec: Filter specification

        Returns:
            Filtered lazy DataFrame
        """
        import polars as pl

        col = pl.col(filter_spec.column)

        if filter_spec.op == FilterOp.EQ:
            return lazy_df.filter(col.eq(filter_spec.value))
        elif filter_spec.op == FilterOp.NE:
            return lazy_df.filter(col.ne(filter_spec.value))
        elif filter_spec.op == FilterOp.GT:
            return lazy_df.filter(col.gt(filter_spec.value))
        elif filter_spec.op == FilterOp.GTE:
            return lazy_df.filter(col.ge(filter_spec.value))
        elif filter_spec.op == FilterOp.LT:
            return lazy_df.filter(col.lt(filter_spec.value))
        elif filter_spec.op == FilterOp.LTE:
            return lazy_df.filter(col.le(filter_spec.value))
        elif filter_spec.op == FilterOp.CONTAINS:
            return lazy_df.filter(col.str.contains(filter_spec.value, literal=True))
        elif filter_spec.op == FilterOp.STARTS_WITH:
            return lazy_df.filter(col.str.starts_with(filter_spec.value))
        elif filter_spec.op == FilterOp.ENDS_WITH:
            return lazy_df.filter(col.str.ends_with(filter_spec.value))
        elif filter_spec.op == FilterOp.IN:
            return lazy_df.filter(col.is_in(filter_spec.value))
        elif filter_spec.op == FilterOp.IS_NULL:
            return lazy_df.filter(col.is_null())
        elif filter_spec.op == FilterOp.IS_NOT_NULL:
            return lazy_df.filter(col.is_not_null())
        else:
            raise QueryExecutorError(f"Unsupported filter operator: {filter_spec.op}")

    def _apply_sorts(self, lazy_df: pl.LazyFrame, sort_specs: list[Any]) -> pl.LazyFrame:
        """Apply multiple sorts to a lazy DataFrame.

        Args:
            lazy_df: Lazy DataFrame
            sort_specs: List of sort specifications

        Returns:
            Sorted lazy DataFrame
        """
        by = [s.column for s in sort_specs]
        descending = [s.direction == SortDirection.DESC for s in sort_specs]
        return lazy_df.sort(by, descending=descending)

    def _apply_groupby(self, lazy_df: pl.LazyFrame, groupby_spec: Any) -> pl.LazyFrame:
        """Apply groupby and aggregations to a lazy DataFrame.

        Args:
            lazy_df: Lazy DataFrame
            groupby_spec: GroupBy specification

        Returns:
            Grouped and aggregated lazy DataFrame
        """
        import polars as pl

        # Build aggregation expressions
        agg_exprs = []
        for agg in groupby_spec.aggregations:
            if agg.func == AggFunc.COUNT and agg.column == "*":
                # COUNT(*) - count all rows
                agg_exprs.append(pl.len().alias(agg.alias))
            else:
                # Map aggregation function
                polars_agg = self._AGG_FUNCS.get(agg.func)
                if not polars_agg:
                    raise QueryExecutorError(f"Unsupported aggregation function: {agg.func}")
                agg_exprs.append(getattr(pl.col(agg.column), polars_agg)().alias(agg.alias))

        # Apply groupby
        return lazy_df.group_by(groupby_spec.columns).agg(agg_exprs)

    def execute_csv(
        self, csv_path: str, query: Query, has_header: bool = True
    ) -> pl.DataFrame:
        """Execute a query against a CSV file using scan_csv.

        This is useful for disk-backed tables that don't fit in memory.

        Args:
            csv_path: Path to CSV file
            query: Query specification
            has_header: Whether CSV has header row

        Returns:
            Result DataFrame after applying query operations

        Raises:
            ValidationError: If query validation fails and validate=True
            QueryExecutorError: If execution fails
        """
        import polars as pl

        # Read header to build schema for validation
        if self.validate and has_header:
            from .query_model import TableSchema

            try:
                # Read just the header to get column names
                header_df = pl.read_csv(csv_path, has_header=True, n_rows=0)
                schema = TableSchema({col: str(dtype) for col, dtype in zip(header_df.columns, header_df.dtypes)})
                is_valid, errors = query.validate(schema)
                if not is_valid:
                    raise ValidationError(f"Query validation failed: {'; '.join(errors)}")
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise
                # If we can't read the file for validation, continue and let it fail during execution
                pass

        # Scan CSV lazily
        lazy_df = pl.scan_csv(csv_path, has_header=has_header)

        # Apply query operations directly on lazy frame
        for f in query.filters:
            lazy_df = self._apply_filter(lazy_df, f)

        if query.groupby:
            lazy_df = self._apply_groupby(lazy_df, query.groupby)

        if query.sort:
            lazy_df = self._apply_sorts(lazy_df, query.sort)

        if query.offset:
            lazy_df = lazy_df.slice(query.offset)

        if query.limit is not None:
            lazy_df = lazy_df.limit(query.limit)

        try:
            return lazy_df.collect()
        except Exception as e:
            raise QueryExecutorError(f"CSV query execution failed: {e}") from e


class DuckDBQueryExecutor:
    """Execute SQL queries against data using DuckDB.

    Supports both in-memory tables (Polars/PyArrow) and CSV files.
    Only allows SELECT queries for safety (read-only mode).

    Examples:
        >>> import polars as pl
        >>> from mytt_scraper.utils.query_executor import DuckDBQueryExecutor
        >>>
        >>> df = pl.DataFrame({"name": ["Alice", "Bob"], "ttr": [1500, 1600]})
        >>> executor = DuckDBQueryExecutor()
        >>> result = executor.execute_sql(df, "SELECT * FROM data WHERE ttr > 1550")
    """

    # Regex to detect unsafe SQL statements (basic guard)
    # Matches INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, etc. at word boundaries
    _UNSAFE_PATTERN = re.compile(
        r"^\s*(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE|UPSERT|ATTACH|DETACH|COPY|EXPORT|IMPORT|LOAD|INSTALL)",
        re.IGNORECASE,
    )

    def __init__(self, validate: bool = True, max_rows: int = 1000) -> None:
        """Initialize the executor.

        Args:
            validate: Whether to validate queries before execution
            max_rows: Maximum rows to return (safety limit)
        """
        self.validate = validate
        self.max_rows = max_rows

    def _validate_select_only(self, sql: str) -> None:
        """Validate that the SQL query is a SELECT statement.

        Args:
            sql: SQL query string

        Raises:
            UnsafeQueryError: If query contains non-SELECT statements
        """
        # Check for unsafe keywords at the start
        if self._UNSAFE_PATTERN.match(sql):
            raise UnsafeQueryError(
                "Only SELECT queries are allowed. "
                "Found unsafe SQL statement."
            )

        # Additional check: must start with SELECT (allowing for whitespace and comments)
        # Remove C-style comments first
        cleaned = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
        # Remove line comments
        cleaned = re.sub(r"--.*?$", "", cleaned, flags=re.MULTILINE)
        # Check if starts with SELECT
        if not re.match(r"^\s*SELECT\s", cleaned, re.IGNORECASE):
            raise UnsafeQueryError(
                "Only SELECT queries are allowed. Query must start with SELECT."
            )

    def execute_sql(
        self, data: pl.DataFrame | Any, sql: str, table_name: str = "data"
    ) -> pl.DataFrame:
        """Execute a SQL query against in-memory data.

        Args:
            data: Polars DataFrame or PyArrow Table to query
            sql: SQL query string (SELECT only)
            table_name: Name to register the data as in DuckDB

        Returns:
            Result DataFrame

        Raises:
            UnsafeQueryError: If query is not a SELECT statement
            QueryExecutorError: If execution fails
        """
        import duckdb
        import polars as pl

        if self.validate:
            self._validate_select_only(sql)

        con = None
        try:
            # Create a connection
            con = duckdb.connect(":memory:")

            # Register the data
            if hasattr(data, "to_arrow"):
                # Polars DataFrame - convert to Arrow for DuckDB
                arrow_data = data.to_arrow()
                con.register(table_name, arrow_data)
            elif hasattr(data, "schema") and hasattr(data, "column_names"):
                # PyArrow Table
                con.register(table_name, data)
            else:
                # Assume it's already something DuckDB can handle
                con.register(table_name, data)

            # Execute query with row limit
            limited_sql = f"SELECT * FROM ({sql}) LIMIT {self.max_rows}"
            result = con.execute(limited_sql).fetch_arrow_table()

            # Convert back to Polars
            return pl.from_arrow(result)

        except UnsafeQueryError:
            raise
        except Exception as e:
            raise QueryExecutorError(f"SQL execution failed: {e}") from e
        finally:
            if con is not None:
                con.close()

    def execute_sql_csv(
        self, csv_path: str, sql: str, table_name: str = "data"
    ) -> pl.DataFrame:
        """Execute a SQL query against a CSV file.

        Uses DuckDB's native CSV reading capabilities.

        Args:
            csv_path: Path to CSV file
            sql: SQL query string (SELECT only)
            table_name: Name to use for the CSV table in the query

        Returns:
            Result DataFrame

        Raises:
            UnsafeQueryError: If query is not a SELECT statement
            QueryExecutorError: If execution fails
        """
        import duckdb
        import polars as pl

        if self.validate:
            self._validate_select_only(sql)

        con = None
        try:
            # Create a connection
            con = duckdb.connect(":memory:")

            # Create a view for the CSV file
            # Escape single quotes in path to prevent SQL injection
            safe_csv_path = csv_path.replace("'", "''")
            con.execute(f"CREATE VIEW {table_name} AS SELECT * FROM read_csv_auto('{safe_csv_path}')")

            # Execute query with row limit
            limited_sql = f"SELECT * FROM ({sql}) LIMIT {self.max_rows}"
            result = con.execute(limited_sql).fetch_arrow_table()

            # Convert back to Polars
            return pl.from_arrow(result)

        except UnsafeQueryError:
            raise
        except Exception as e:
            raise QueryExecutorError(f"SQL execution failed: {e}") from e
        finally:
            if con is not None:
                con.close()


def create_executor(backend: str = "polars", **kwargs: Any) -> PolarsQueryExecutor | DuckDBQueryExecutor:
    """Factory function to create a query executor.

    Args:
        backend: Backend type ("polars" or "duckdb")
        **kwargs: Additional arguments passed to executor constructor

    Returns:
        Query executor instance

    Raises:
        ValueError: If backend is not supported
    """
    if backend == "polars":
        return PolarsQueryExecutor(**kwargs)
    elif backend == "duckdb":
        return DuckDBQueryExecutor(**kwargs)
    else:
        raise ValueError(f"Unsupported backend: {backend!r}. Use 'polars' or 'duckdb'.")
