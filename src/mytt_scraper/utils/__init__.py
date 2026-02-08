"""Utility modules for mytt_scraper"""

from .helpers import parse_multipart_json
from .in_memory_tables import extract_flat_tables
from .query_executor import PolarsQueryExecutor, QueryExecutorError, ValidationError, create_executor
from .query_model import (
    AggFunc,
    Aggregation,
    Backend,
    Filter,
    FilterOp,
    GroupBy,
    Query,
    Sort,
    SortDirection,
    TableSchema,
)
from .table_extractor import (
    extract_club_info_table,
    extract_league_table,
    extract_ttr_history_events_table,
    extract_ttr_history_matches_table,
    extract_ttr_rankings_table,
    write_csv,
)
from .table_provider import (
    DiskTableProvider,
    InMemoryTableProvider,
    TableInfo,
    TableProvider,
    TableSource,
    create_default_provider,
)

__all__ = [
    "parse_multipart_json",
    "extract_club_info_table",
    "extract_ttr_rankings_table",
    "extract_league_table",
    "extract_ttr_history_events_table",
    "extract_ttr_history_matches_table",
    "write_csv",
    "extract_flat_tables",
    # Query model
    "AggFunc",
    "Aggregation",
    "Backend",
    "Filter",
    "FilterOp",
    "GroupBy",
    "Query",
    "Sort",
    "SortDirection",
    "TableSchema",
    # Query executor
    "PolarsQueryExecutor",
    "QueryExecutorError",
    "ValidationError",
    "create_executor",
    # Table provider
    "DiskTableProvider",
    "InMemoryTableProvider",
    "TableInfo",
    "TableProvider",
    "TableSource",
    "create_default_provider",
]
