"""Table provider abstraction for discovering and accessing tables.

Provides a unified interface for accessing tables from multiple sources:
- In-memory tables (Polars DataFrames / PyArrow Tables from current session)
- Disk-based tables (CSV files in tables/ directory)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Protocol


class TableSource(Enum):
    """Source of a table."""
    MEMORY = auto()
    DISK = auto()


@dataclass(frozen=True)
class TableInfo:
    """Metadata about a discovered table.
    
    Attributes:
        name: Internal table identifier (e.g., "ttr_rankings", "abc123_ttr_rankings")
        display_name: Human-friendly display label (e.g., "TTR Rankings", "abc123 - TTR Rankings")
        table_type: Detected table type/category (e.g., "ttr_rankings", "league_table")
        source: Source of the table (MEMORY or DISK)
        source_hint: Additional source info (e.g., "in-memory", "tables/abc123_ttr_rankings.csv")
        row_count: Number of rows (if available, -1 if unknown)
        prefix: Optional prefix from filename (e.g., "abc123" from "abc123_ttr_rankings.csv")
    """
    name: str
    display_name: str
    table_type: str
    source: TableSource
    source_hint: str
    row_count: int = -1
    prefix: str = ""


class TableDataProvider(Protocol):
    """Protocol for table data access.
    
    Implementations provide access to actual table data for a given table name.
    """
    
    def get_data(self, name: str) -> Any | None:
        """Get table data by name.
        
        Args:
            name: Table identifier (from TableInfo.name)
            
        Returns:
            Table data (Polars DataFrame, PyArrow Table, etc.) or None if not found
        """
        ...
    
    def has_table(self, name: str) -> bool:
        """Check if a table exists.
        
        Args:
            name: Table identifier
            
        Returns:
            True if the table exists, False otherwise
        """
        ...


class InMemoryTableProvider:
    """Provider for in-memory tables stored in app state.
    
    These are tables extracted from recent fetch operations and stored
    as Polars DataFrames or PyArrow Tables.
    """
    
    # Known table types with their display names
    KNOWN_TABLE_TYPES: dict[str, str] = {
        "ttr_rankings": "TTR Rankings",
        "league_table": "League Table",
        "club_info": "Club Info",
        "ttr_history_events": "TTR History Events",
        "ttr_history_matches": "TTR History Matches",
        "tournament_registrations": "Tournament Registrations",
    }
    
    def __init__(self, tables: dict[str, Any] | None = None) -> None:
        """Initialize with optional pre-existing tables dict.
        
        Args:
            tables: Dictionary mapping table names to DataFrame/Table objects
        """
        self._tables = tables or {}
    
    def update_tables(self, tables: dict[str, Any]) -> None:
        """Update the stored tables.
        
        Args:
            tables: New tables dictionary
        """
        self._tables = tables
    
    def discover(self) -> list[TableInfo]:
        """Discover all in-memory tables.
        
        Returns:
            List of TableInfo objects for available in-memory tables
        """
        discovered: list[TableInfo] = []
        
        for name, data in self._tables.items():
            table_type, prefix = self._detect_table_type(name)
            display_name = self._build_display_name(table_type, prefix)
            
            # Get row count if available
            row_count = -1
            if hasattr(data, "__len__"):
                try:
                    row_count = len(data)
                except Exception:
                    pass
            # Polars DataFrame
            if hasattr(data, "height"):
                row_count = data.height
            # PyArrow Table
            elif hasattr(data, "num_rows"):
                row_count = data.num_rows
            
            info = TableInfo(
                name=name,
                display_name=display_name,
                table_type=table_type,
                source=TableSource.MEMORY,
                source_hint="in-memory",
                row_count=row_count,
                prefix=prefix,
            )
            discovered.append(info)
        
        return discovered
    
    def get_data(self, name: str) -> Any | None:
        """Get in-memory table data by name.
        
        Args:
            name: Table name
            
        Returns:
            Table data or None if not found
        """
        return self._tables.get(name)
    
    def has_table(self, name: str) -> bool:
        """Check if an in-memory table exists.
        
        Args:
            name: Table name
            
        Returns:
            True if the table exists in memory
        """
        return name in self._tables
    
    def _detect_table_type(self, name: str) -> tuple[str, str]:
        """Detect table type and prefix from name.
        
        Args:
            name: Table name (e.g., "ttr_rankings", "abc123_ttr_rankings")
            
        Returns:
            Tuple of (table_type, prefix)
        """
        # Check for prefix pattern: "{prefix}_{table_type}"
        parts = name.rsplit("_", 1)
        if len(parts) == 2:
            prefix, suffix = parts
            # If suffix is a known type, use it
            if suffix in self.KNOWN_TABLE_TYPES:
                return suffix, prefix
            # Check full name as well (for names like "club_info" where "info" isn't a type)
            if name in self.KNOWN_TABLE_TYPES:
                return name, ""
        
        # Check if the full name is a known type
        if name in self.KNOWN_TABLE_TYPES:
            return name, ""
        
        # Check for multi-part table types (e.g., "ttr_history_events")
        for known_type in sorted(self.KNOWN_TABLE_TYPES.keys(), key=len, reverse=True):
            if name.endswith(known_type):
                prefix = name[: -(len(known_type) + 1)]  # +1 for underscore
                return known_type, prefix
        
        # Unknown type - use the name as-is
        return name, ""
    
    def _build_display_name(self, table_type: str, prefix: str) -> str:
        """Build a human-friendly display name.
        
        Args:
            table_type: Detected table type
            prefix: Optional prefix (e.g., user ID)
            
        Returns:
            Display name like "TTR Rankings" or "abc123 - TTR Rankings"
        """
        base_name = self.KNOWN_TABLE_TYPES.get(table_type, table_type.replace("_", " ").title())
        
        if prefix:
            return f"{prefix} - {base_name}"
        return base_name


class DiskTableProvider:
    """Provider for disk-based tables (CSV files).
    
    Scans the tables/ directory for CSV files and provides metadata-only
    access until the actual data is requested.
    """
    
    # Same known types as InMemoryTableProvider
    KNOWN_TABLE_TYPES: dict[str, str] = InMemoryTableProvider.KNOWN_TABLE_TYPES
    
    def __init__(self, tables_dir: str | Path = "tables") -> None:
        """Initialize with tables directory path.
        
        Args:
            tables_dir: Path to the tables directory (default: "tables")
        """
        self._tables_dir = Path(tables_dir)
    
    def discover(self) -> list[TableInfo]:
        """Discover all CSV files in the tables directory.
        
        Does not load full table data - only reads metadata (row count via
        fast line counting when possible).
        
        Returns:
            List of TableInfo objects for available CSV files
        """
        discovered: list[TableInfo] = []
        
        if not self._tables_dir.exists():
            return discovered
        
        for csv_file in sorted(self._tables_dir.glob("*.csv")):
            info = self._analyze_csv_file(csv_file)
            if info:
                discovered.append(info)
        
        return discovered
    
    def get_data(self, name: str) -> Path | None:
        """Get the path to a CSV file by table name.
        
        Args:
            name: Table name (filename without .csv extension)
            
        Returns:
            Path to the CSV file or None if not found
        """
        csv_path = self._tables_dir / f"{name}.csv"
        if csv_path.exists():
            return csv_path
        return None
    
    def has_table(self, name: str) -> bool:
        """Check if a CSV file exists for the given table name.
        
        Args:
            name: Table name
            
        Returns:
            True if the CSV file exists
        """
        return (self._tables_dir / f"{name}.csv").exists()
    
    def _analyze_csv_file(self, csv_path: Path) -> TableInfo | None:
        """Analyze a CSV file and create TableInfo.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            TableInfo or None if analysis fails
        """
        name = csv_path.stem  # filename without extension
        table_type, prefix = self._detect_table_type(name)
        display_name = self._build_display_name(table_type, prefix)
        
        # Fast row count: count newlines without parsing
        row_count = self._fast_count_rows(csv_path)
        
        return TableInfo(
            name=name,
            display_name=display_name,
            table_type=table_type,
            source=TableSource.DISK,
            source_hint=f"tables/{csv_path.name}",
            row_count=row_count,
            prefix=prefix,
        )
    
    def _fast_count_rows(self, csv_path: Path) -> int:
        """Count rows in a CSV file efficiently.
        
        Uses line counting (subtracting header) for fast metadata-only access.
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Row count or -1 if counting fails
        """
        try:
            with open(csv_path, "rb") as f:
                # Count newlines efficiently
                chunk_size = 1024 * 1024  # 1MB chunks
                newline_count = 0
                
                while chunk := f.read(chunk_size):
                    newline_count += chunk.count(b"\n")
                
                # Subtract 1 for header row (if file has content)
                # If file ends with newline, newline_count includes it
                return max(0, newline_count - 1)
        except Exception:
            return -1
    
    def _detect_table_type(self, name: str) -> tuple[str, str]:
        """Detect table type and prefix from filename.
        
        Args:
            name: Filename stem (e.g., "ttr_rankings", "abc123_ttr_rankings")
            
        Returns:
            Tuple of (table_type, prefix)
        """
        # Check for prefix pattern: "{prefix}_{table_type}"
        for known_type in sorted(self.KNOWN_TABLE_TYPES.keys(), key=len, reverse=True):
            if name.endswith(known_type):
                if name == known_type:
                    return known_type, ""
                # Has prefix
                prefix = name[: -(len(known_type) + 1)]  # +1 for underscore
                return known_type, prefix
        
        # Unknown type - use the name as-is
        return name, ""
    
    def _build_display_name(self, table_type: str, prefix: str) -> str:
        """Build a human-friendly display name.
        
        Args:
            table_type: Detected table type
            prefix: Optional prefix (e.g., user ID)
            
        Returns:
            Display name like "TTR Rankings" or "abc123 - TTR Rankings"
        """
        base_name = self.KNOWN_TABLE_TYPES.get(table_type, table_type.replace("_", " ").title())
        
        if prefix:
            return f"{prefix} - {base_name}"
        return base_name


class TableProvider:
    """Unified table provider that combines in-memory and disk sources.
    
    Provides a single interface for discovering and accessing tables from
    both in-memory (current session) and disk (CSV files) sources.
    
    Discovery order:
    1. In-memory tables (preferred, reflects current session state)
    2. Disk tables (fallback for tables not in memory)
    
    Duplicate handling:
    - In-memory tables take precedence over disk tables
    - Disk tables with the same name are filtered out if present in memory
    """
    
    def __init__(
        self,
        memory_provider: InMemoryTableProvider | None = None,
        disk_provider: DiskTableProvider | None = None,
    ) -> None:
        """Initialize with optional providers.
        
        Args:
            memory_provider: Provider for in-memory tables
            disk_provider: Provider for disk-based tables
        """
        self._memory = memory_provider or InMemoryTableProvider()
        self._disk = disk_provider or DiskTableProvider()
    
    def discover(self, include_disk: bool = True) -> list[TableInfo]:
        """Discover all available tables.
        
        Args:
            include_disk: Whether to include disk-based tables (default: True)
        
        Returns:
            Combined list of TableInfo objects from all sources.
            In-memory tables are listed first, followed by disk tables
            not already present in memory.
        """
        # Get in-memory tables first
        memory_tables = self._memory.discover()
        memory_names = {t.name for t in memory_tables}
        
        result = list(memory_tables)
        
        # Add disk tables that aren't in memory
        if include_disk:
            disk_tables = self._disk.discover()
            for disk_table in disk_tables:
                if disk_table.name not in memory_names:
                    result.append(disk_table)
        
        return result
    
    def get_table_info(self, name: str) -> TableInfo | None:
        """Get metadata for a specific table.
        
        Checks in-memory first, then disk.
        
        Args:
            name: Table name
            
        Returns:
            TableInfo or None if not found
        """
        # Check in-memory first
        if self._memory.has_table(name):
            for info in self._memory.discover():
                if info.name == name:
                    return info
        
        # Check disk
        if self._disk.has_table(name):
            for info in self._disk.discover():
                if info.name == name:
                    return info
        
        return None
    
    def get_data(self, name: str) -> tuple[Any, TableSource] | None:
        """Get table data with source information.
        
        Checks in-memory first, then disk.
        
        Args:
            name: Table name
            
        Returns:
            Tuple of (data, source) or None if not found.
            Data is Polars DataFrame/PyArrow Table for memory,
            or Path for disk (caller should load the CSV).
        """
        # Check in-memory first
        memory_data = self._memory.get_data(name)
        if memory_data is not None:
            return (memory_data, TableSource.MEMORY)
        
        # Check disk
        disk_path = self._disk.get_data(name)
        if disk_path is not None:
            return (disk_path, TableSource.DISK)
        
        return None
    
    def has_table(self, name: str) -> bool:
        """Check if a table exists in any source.
        
        Args:
            name: Table name
            
        Returns:
            True if the table exists in memory or on disk
        """
        return self._memory.has_table(name) or self._disk.has_table(name)
    
    def update_memory_tables(self, tables: dict[str, Any]) -> None:
        """Update the in-memory tables.
        
        Args:
            tables: New tables dictionary
        """
        self._memory.update_tables(tables)
    
    def set_tables_dir(self, tables_dir: str | Path) -> None:
        """Update the disk tables directory.
        
        Args:
            tables_dir: New tables directory path
        """
        self._disk = DiskTableProvider(tables_dir)


def create_default_provider(
    memory_tables: dict[str, Any] | None = None,
    tables_dir: str | Path = "tables",
) -> TableProvider:
    """Create a TableProvider with default configuration.
    
    Args:
        memory_tables: Optional in-memory tables dictionary
        tables_dir: Path to tables directory
        
    Returns:
        Configured TableProvider instance
    """
    memory_provider = InMemoryTableProvider(memory_tables)
    disk_provider = DiskTableProvider(tables_dir)
    return TableProvider(memory_provider, disk_provider)
