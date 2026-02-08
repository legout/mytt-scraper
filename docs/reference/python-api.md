# Python API Reference

Complete reference for using `mytt-scraper` as a Python library.

## Overview

The Python API provides programmatic access to mytischtennis.de data extraction. Use it for:

- **REPL/Notebook exploration** — Interactive data analysis
- **Scripting** — Automate data collection
- **Integration** — Embed in larger applications
- **Custom workflows** — Combine with Polars, Pandas, or DuckDB

---

## Installation

```bash
pip install mytt-scraper
```

Optional dependencies for specific backends:

```bash
pip install polars      # Recommended for in-memory tables
pip install pandas      # Alternative backend
pip install pyarrow     # Arrow-native backend
pip install duckdb      # For SQL queries on disk files
```

---

## Quick Start

```python
from mytt_scraper import MyTischtennisScraper

# Initialize scraper
scraper = MyTischtennisScraper(
    username="user@example.com",
    password="your-password",
    headless=True  # Set False to see browser
)

# Login and fetch data
if scraper.login():
    data, remaining = scraper.fetch_own_community()
    
    # Extract tables as Polars DataFrames
    tables = scraper.extract_flat_tables(data, remaining, backend="polars")
    
    # Access individual tables
    rankings = tables["ttr_rankings"]
    print(rankings.head())
```

---

## MyTischtennisScraper

Main class for fetching data from mytischtennis.de.

### Constructor

```python
MyTischtennisScraper(
    username: str,
    password: str,
    headless: bool = True,
    tables_dir: Optional[Path] = None
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | `str` | Required | Email address for login |
| `password` | `str` | Required | Password for login |
| `headless` | `bool` | `True` | Run browser without visible window |
| `tables_dir` | `Optional[Path]` | `"tables"` | Directory for CSV output |

### Methods

#### `login() -> bool`

Authenticate with mytischtennis.de using Playwright browser automation.

**Returns:** `True` if login successful, `False` otherwise.

**Example:**
```python
scraper = MyTischtennisScraper("user@example.com", "password")
if not scraper.login():
    raise RuntimeError("Login failed")
```

---

#### `fetch_own_community() -> Tuple[Optional[Dict[str, Any]], Optional[str]]`

Fetch your own community/profile data including TTR rankings and league tables.

**Returns:** Tuple of `(data, remaining)` where:
- `data`: Parsed JSON response (dict) or `None` if request failed
- `remaining`: Deferred TTR history data as raw string or `None` if no deferred data

**Example:**
```python
data, remaining = scraper.fetch_own_community()
print(f"Fetched {len(data.get('pageContent', {}))} page sections")
```

---

#### `fetch_external_profile(user_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]`

Fetch data for a specific player by user-id.

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | `str` | Player's UUID (e.g., `"2fa35076-e634-457c-bf70-e89a70e0b7b0"`) |

**Returns:** Same format as `fetch_own_community()`

**Example:**
```python
user_id = "2fa35076-e634-457c-bf70-e89a70e0b7b0"
data, remaining = scraper.fetch_external_profile(user_id)
```

---

#### `extract_flat_tables(data, remaining, backend="polars") -> Dict[str, Any]`

Extract normalized tables from fetched data as in-memory objects.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `Dict[str, Any]` | Required | Main response data from fetch methods |
| `remaining` | `Optional[str]` | `None` | Deferred TTR history data |
| `backend` | `"polars" \| "pandas" \| "pyarrow"` | `"polars"` | Output format |

**Returns:** Dictionary mapping table names to DataFrame/Table objects.

| Table Name | Description | Availability |
|------------|-------------|--------------|
| `club_info` | Club information and league details | Always |
| `ttr_rankings` | TTR rankings for club members | Always |
| `league_table` | Current league standings | Always |
| `ttr_history_events` | TTR history events summary | If `remaining` provided |
| `ttr_history_matches` | Individual matches per event | If `remaining` provided |

**Raises:**
- `ValueError`: If unsupported backend specified

**Example:**
```python
# Polars backend (recommended)
import polars as pl

tables = scraper.extract_flat_tables(data, remaining, backend="polars")
df = tables["ttr_rankings"]
print(df.filter(pl.col("rank") > 1500))

# Pandas backend
import pandas as pd

tables = scraper.extract_flat_tables(data, remaining, backend="pandas")
df = tables["ttr_rankings"]
print(df[df["rank"] > 1500])
```

---

#### `extract_and_save_tables(data, remaining=None, prefix="") -> None`

Extract tables and save to CSV files (disk-based workflow).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `Dict[str, Any]` | Required | Response data |
| `remaining` | `Optional[str]` | `None` | TTR history data |
| `prefix` | `str` | `""` | Filename prefix (e.g., `"user123_"`) |

**Output files:** Saved to `tables_dir` (constructor parameter):
- `{prefix}club_info.csv`
- `{prefix}ttr_rankings.csv`
- `{prefix}league_table.csv`
- `{prefix}ttr_history_events.csv`
- `{prefix}ttr_history_matches.csv`

**Example:**
```python
# Save with prefix for external profile
scraper.extract_and_save_tables(data, remaining, prefix="external_user_")
# Creates: tables/external_user_ttr_rankings.csv
```

---

#### `run_own_profile() -> Optional[Dict[str, Any]]`

Complete workflow: login, fetch own data, extract and save tables.

**Returns:** Profile data if successful, `None` otherwise.

**Example:**
```python
data = scraper.run_own_profile()
if data:
    print("Profile data saved to tables/")
```

---

#### `run_external_profile(user_id: str, prefix=None) -> Optional[Dict[str, Any]]`

Complete workflow for external profile.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | `str` | Required | Player's user-id |
| `prefix` | `Optional[str]` | `user_id + "_"` | Filename prefix |

**Example:**
```python
data = scraper.run_external_profile("2fa35076-...", prefix="player_")
```

---

#### `run_multiple_profiles(user_ids: List[str]) -> Dict[str, Any]`

Batch fetch multiple profiles.

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_ids` | `List[str]` | List of user-ids to fetch |

**Returns:** Dictionary mapping user-ids to their data.

**Example:**
```python
user_ids = ["id1", "id2", "id3"]
results = scraper.run_multiple_profiles(user_ids)
for uid, data in results.items():
    print(f"{uid}: {'OK' if data else 'Failed'}")
```

---

## PlayerSearcher

Extends `MyTischtennisScraper` with player search functionality.

### Constructor

Inherits from `MyTischtennisScraper` — same parameters.

```python
from mytt_scraper import PlayerSearcher

searcher = PlayerSearcher("user@example.com", "password")
```

### Methods

#### `search_players(query: str, use_playwright: bool = False) -> List[Dict[str, Any]]`

Search for players by name, club, or other criteria.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | Search term |
| `use_playwright` | `bool` | `False` | Use browser for search |

**Returns:** List of player dictionaries with fields:
- `user_id` / `personId`: Player identifier
- `name` / `firstname` / `lastname`: Player name
- `club` / `clubName`: Club name
- `ttr`: TTR rating

**Search Methods:**
- `use_playwright=False`: API search (faster)
- `use_playwright=True`: Browser search (more reliable)

**Example:**
```python
results = searcher.search_players("Müller", use_playwright=False)
for player in results:
    print(f"{player['name']} - {player['club']} (TTR: {player['ttr']})")
```

---

#### `run_search_mode() -> None`

Interactive search mode (CLI-like experience in Python).

Prompts for search queries and displays results interactively.

**Example:**
```python
searcher.login()
searcher.run_search_mode()  # Interactive prompts
```

---

#### `run_search_and_fetch_mode() -> None`

Search and fetch selected players in one operation.

Interactive prompts for:
1. Search query
2. Search method (API/Playwright)
3. Selection (indices or "all")

**Example:**
```python
searcher.login()
searcher.run_search_and_fetch_mode()  # Interactive workflow
```

---

## extract_flat_tables

Module-level function for extracting tables from raw data.

```python
from mytt_scraper.utils import extract_flat_tables

tables = extract_flat_tables(data, remaining, backend="polars")
```

This is equivalent to the instance method but can be used without a scraper instance when working with cached data.

---

## In-Memory Table Workflows

### Workflow 1: Direct Analysis

Extract data and analyze immediately in memory:

```python
import polars as pl
from mytt_scraper import MyTischtennisScraper

scraper = MyTischtennisScraper("user@example.com", "password")
scraper.login()

data, remaining = scraper.fetch_own_community()
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Analyze without saving to disk
rankings = tables["ttr_rankings"]
top_players = rankings.filter(pl.col("rank") > 1600)
print(top_players.select(["firstname", "lastname", "rank"]))
```

### Workflow 2: Polars from In-Memory

Load extracted tables into Polars DataFrames:

```python
import polars as pl

# After extraction
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Each table is already a Polars DataFrame
df_rankings = tables["ttr_rankings"]
df_events = tables["ttr_history_events"]

# Query with Polars DSL
recent_events = df_events.filter(
    pl.col("event_date_time") > "2024-01-01"
)
```

### Workflow 3: Polars from Disk (CSV)

Load previously saved CSV files with Polars:

```python
import polars as pl
from pathlib import Path

# Load from default tables directory
tables_dir = Path("tables")

rankings = pl.read_csv(tables_dir / "ttr_rankings.csv")
events = pl.read_csv(tables_dir / "ttr_history_events.csv")
matches = pl.read_csv(tables_dir / "ttr_history_matches.csv")

# Join tables
results = matches.join(
    events.select(["event_id", "event_name", "ttr_before", "ttr_after"]),
    on="event_id",
    how="left"
)
```

### Workflow 4: DuckDB from Disk

Use DuckDB for SQL queries on CSV files:

```python
import duckdb

con = duckdb.connect()

# Query CSV directly with SQL
result = con.execute("""
    SELECT 
        firstname,
        lastname,
        rank,
        matchCount
    FROM read_csv_auto('tables/ttr_rankings.csv')
    WHERE rank > 1500
    ORDER BY rank DESC
""").fetchdf()

# Join multiple CSVs
result = con.execute("""
    SELECT 
        m.event_name,
        m.own_person_name,
        m.other_person_name,
        m.own_sets,
        m.other_sets
    FROM read_csv_auto('tables/ttr_history_matches.csv') m
    JOIN read_csv_auto('tables/ttr_history_events.csv') e
        ON m.event_id = e.event_id
    WHERE e.ttr_delta > 0
""").fetchdf()
```

---

## Table Schemas

See [Table Schemas](table-schemas.md) for complete field documentation.

Quick reference for column names:

| Table | Key Columns |
|-------|-------------|
| `club_info` | `clubNr`, `association`, `season`, `group_name` |
| `ttr_rankings` | `firstname`, `lastname`, `rank`, `matchCount` |
| `league_table` | `table_rank`, `teamname`, `own_points` |
| `ttr_history_events` | `event_name`, `ttr_before`, `ttr_after`, `ttr_delta` |
| `ttr_history_matches` | `own_person_name`, `other_person_name`, `own_sets`, `other_sets` |

---

## Error Handling

Common exceptions and how to handle them:

```python
from mytt_scraper import MyTischtennisScraper

scraper = MyTischtennisScraper("user@example.com", "password")

# Login failures
if not scraper.login():
    print("Login failed - check credentials")
    exit(1)

# Invalid backend
try:
    tables = scraper.extract_flat_tables(data, remaining, backend="invalid")
except ValueError as e:
    print(f"Invalid backend: {e}")

# Missing tables (graceful handling)
tables = scraper.extract_flat_tables(data, remaining)
if "ttr_history_events" not in tables:
    print("No TTR history available")
```

---

## Complete Example: REPL Session

```python
# In a Python REPL or Jupyter notebook

import polars as pl
from mytt_scraper import MyTischtennisScraper

# Initialize
scraper = MyTischtennisScraper("user@example.com", "password", headless=True)

# Login
assert scraper.login(), "Login failed"

# Fetch data
data, remaining = scraper.fetch_own_community()

# Extract as Polars DataFrames
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Explore
rankings = tables["ttr_rankings"]
rankings.head()

# Query
high_ranked = rankings.filter(pl.col("rank") > 1600)
high_ranked.select(["position", "firstname", "lastname", "rank", "matchCount"])

# Analyze TTR history
events = tables["ttr_history_events"]
total_change = events["ttr_delta"].sum()
print(f"Total TTR change: {total_change:+,}")

# Visualize (if matplotlib installed)
import matplotlib.pyplot as plt

events_sorted = events.sort("event_date_time")
plt.plot(events_sorted["ttr_after"])
plt.title("TTR Over Time")
plt.show()
```

---

## See Also

- [CLI Reference](cli.md) — Command-line interface
- [Table Schemas](table-schemas.md) — Complete field documentation
- [How-To: Search for Players](../how-to/search-players.md) — Step-by-step search guide
- [How-To: Fetch External Profile](../how-to/fetch-external-profile.md) — Profile fetching guide