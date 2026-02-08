# In-Memory vs Disk Tables

This page explains mytt-scraper's dual approach to data handling: extracting tables directly into memory for immediate analysis, or saving to CSV files for persistence and portability.

## The Core Philosophy

**In-memory first, disk when needed.**

Modern data tools (Polars, DuckDB, Pandas) make in-memory analysis incredibly powerful. We prioritize this workflow while keeping CSV export available for compatibility and archiving.

## Two Workflows Compared

### In-Memory Workflow (Recommended)

```python
import polars as pl
from mytt_scraper import MyTischtennisScraper

scraper = MyTischtennisScraper("user@example.com", "password")
scraper.login()

# Fetch and extract directly to DataFrames
data, remaining = scraper.fetch_own_community()
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Analyze immediately — no files written
rankings = tables["ttr_rankings"]
top_players = rankings.filter(pl.col("rank") > 1600)
print(top_players.select(["firstname", "lastname", "rank"]))
```

**Best for:**
- Interactive exploration in REPL/Jupyter
- Quick analysis without file management
- Large datasets where CSV I/O is slow
- Pipeline workflows (extract → transform → load)

### Disk-Based Workflow (CSV)

```python
scraper = MyTischtennisScraper("user@example.com", "password")
scraper.login()

# Fetch and save to CSV files
data, remaining = scraper.fetch_own_community()
scraper.extract_and_save_tables(data, remaining)

# Files created:
# - tables/club_info.csv
# - tables/ttr_rankings.csv
# - tables/league_table.csv
# - tables/ttr_history_events.csv
# - tables/ttr_history_matches.csv
```

**Best for:**
- Sharing data with others
- Archiving historical snapshots
- Using with Excel, R, or other tools
- Situations where you need files on disk

## Why In-Memory First?

### Performance

| Operation | In-Memory | CSV Round-Trip |
|-----------|-----------|----------------|
| Filter 10K rows | ~1ms | ~100ms (read) + ~1ms |
| Sort 10K rows | ~2ms | ~100ms (read) + ~2ms |
| Aggregate | ~1ms | ~100ms (read) + ~1ms |
| Chain 5 operations | ~5ms | ~500ms + overhead |

*Approximate timings on modern hardware with warm filesystem cache*

Eliminating CSV serialization/deserialization provides **10-100x speedup** for iterative analysis.

### Interactivity

In-memory tables enable a fluid workflow:

```python
# Quick exploration without commitment
rankings = tables["ttr_rankings"]

# What's the distribution?
rankings["rank"].describe()

# Who's in the top 10?
rankings.top_k(10, by="rank")

# How does this correlate with match count?
rankings.plot.scatter("rank", "matchCount")  # if plotting available

# Only save if analysis reveals something worth keeping
rankings.write_csv("top_players_analysis.csv")
```

### Modern Tooling

Libraries like **Polars** and **DuckDB** are designed for in-memory processing:

- **Columnar storage** — Efficient for analytical queries
- **Vectorized operations** — SIMD-optimized computations
- **Lazy evaluation** — Query optimization before execution
- **Zero-copy views** — No data duplication for filtering

## CSV Fallback: When Files Make Sense

### Portability

CSV is the **lingua franca** of data:

```bash
# Anyone can open these
libreoffice tables/ttr_rankings.csv  # Excel alternative
R -e "read.csv('tables/ttr_rankings.csv')"  # R
sqlite3 -csv mydb.sqlite ".import tables/ttr_rankings.csv rankings"  # SQLite
```

### Persistence

Files survive process termination:

```python
# Monday: Fetch and save
scraper.extract_and_save_tables(data, remaining, prefix="2025-02-09_")

# Friday: Analyze archived data
import polars as pl
monday_rankings = pl.read_csv("tables/2025-02-09_ttr_rankings.csv")
friday_rankings = pl.read_csv("tables/2025-02-14_ttr_rankings.csv")

# Compare changes
changes = friday_rankings.join(
    monday_rankings,
    on="personId",
    suffix="_monday"
)
```

### Tool Compatibility

Some workflows require files:

- **Version control** — Track `tables/` with Git (for small datasets)
- **Data pipelines** — Airflow, Prefect, or cron jobs expect file outputs
- **Visualization tools** — Tableau, Power BI work best with files

## Backend Options

When using in-memory extraction, you can choose your DataFrame library:

### Polars (Default, Recommended)

```python
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Polars is fast, modern, and expressive
import polars as pl

# Lazy evaluation for large datasets
lazy_df = tables["ttr_rankings"].lazy()
result = lazy_df.filter(pl.col("rank") > 1500).collect()
```

**Pros:** Fastest, modern API, true multithreading  
**Cons:** Newer ecosystem, some pandas features missing

### Pandas

```python
tables = scraper.extract_flat_tables(data, remaining, backend="pandas")

# Familiar, widely used
import pandas as pd

# Rich ecosystem
result = tables["ttr_rankings"].groupby("club").agg({"rank": "mean"})
```

**Pros:** Most familiar, vast ecosystem, best documentation  
**Cons:** Slower, single-threaded, more memory usage

### PyArrow

```python
tables = scraper.extract_flat_tables(data, remaining, backend="pyarrow")

# Interoperability standard
import pyarrow as pa

# Zero-copy conversion to pandas
pandas_df = tables["ttr_rankings"].to_pandas()
```

**Pros:** Zero-copy interop, language-agnostic, efficient  
**Cons:** Lower-level API, less ergonomic for analysis

## DuckDB: SQL on Either

**DuckDB** bridges in-memory and disk workflows by letting you query both:

### Query In-Memory DataFrames

```python
import duckdb
import polars as pl

# Extract to Polars
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Query with SQL
con = duckdb.connect()
result = con.execute("""
    SELECT 
        firstname,
        lastname,
        rank,
        matchCount
    FROM tables['ttr_rankings']
    WHERE rank > 1600
    ORDER BY rank DESC
""").pl()  # Returns Polars DataFrame
```

### Query CSV Files Directly

```python
# No need to load into memory first
result = con.execute("""
    SELECT 
        e.event_name,
        e.ttr_before,
        e.ttr_after,
        COUNT(m.match_number) as match_count
    FROM read_csv_auto('tables/ttr_history_events.csv') e
    LEFT JOIN read_csv_auto('tables/ttr_history_matches.csv') m
        ON e.event_id = m.event_id
    GROUP BY e.event_id, e.event_name, e.ttr_before, e.ttr_after
    ORDER BY e.event_date_time DESC
""").fetchdf()
```

DuckDB is particularly powerful for **joining multiple CSV files** without loading them all into memory simultaneously.

## Decision Flowchart

```
┌─────────────────────────────────────┐
│  What do you need to do with data?  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐  ┌──────────────────┐
│ Interactive  │  │  Share/Archive   │
│  analysis    │  │  or tool export  │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌──────────────┐  ┌──────────────────┐
│ In-memory    │  │    CSV files     │
│ (Polars/     │  │  extract_and_    │
│  Pandas)     │  │  save_tables()   │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌─────────────────────────────────────┐
│     Large dataset or complex SQL?   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐  ┌──────────────────┐
│     Yes      │  │       No         │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌──────────────┐  ┌──────────────────┐
│ Use DuckDB   │  │ You're all set!  │
│ on CSV or    │  │                  │
│ in-memory    │  │                  │
└──────────────┘  └──────────────────┘
```

## Migration Examples

### From Disk to In-Memory

```python
# Before: CSV-based workflow
scraper.extract_and_save_tables(data, remaining)
rankings = pd.read_csv("tables/ttr_rankings.csv")  # Extra I/O

# After: In-memory (faster)
tables = scraper.extract_flat_tables(data, remaining, backend="pandas")
rankings = tables["ttr_rankings"]  # Already a DataFrame
```

### From In-Memory to Disk

```python
# After analysis, save results
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Do your analysis
top_players = tables["ttr_rankings"].filter(pl.col("rank") > 1600)

# Save just what you need
top_players.write_csv("tables/high_ranked_players.csv")
```

### Hybrid Approach

```python
# Fetch once, use both workflows
data, remaining = scraper.fetch_own_community()

# In-memory for immediate analysis
tables = scraper.extract_flat_tables(data, remaining, backend="polars")
analyze(tables["ttr_rankings"])

# Also save to disk for later
scraper.extract_and_save_tables(data, remaining, prefix="backup_")
```

## Missing Tables Behavior

Both workflows handle missing data gracefully:

```python
# TTR history only exists if you've played matches
tables = scraper.extract_flat_tables(data, remaining)

# Check existence before using
if "ttr_history_events" in tables:
    print(f"Found {len(tables['ttr_history_events'])} events")
else:
    print("No TTR history available (no matches played)")
```

Tables are **omitted** rather than empty when data is unavailable. This distinction matters: absence means "not applicable" rather than "zero rows."

## Memory Considerations

### How Much RAM Do You Need?

| Dataset Size | Approx. RAM | Example |
|--------------|-------------|---------|
| Single profile | ~5-10 MB | Your own club data |
| 10 profiles | ~50-100 MB | Small team analysis |
| 100 profiles | ~500 MB - 1 GB | Club comparison |
| 1000 profiles | ~5-10 GB | Large-scale research |

For most personal use cases, in-memory is perfectly feasible. For bulk operations, consider:

- Processing in batches
- Using CSV with DuckDB for out-of-core queries
- Streaming extraction (not yet implemented)

## See Also

- **[Python API Reference](../reference/python-api.md)** — Complete in-memory workflow documentation
- **[How-To: Filter and Query Tables](../how-to/filter-query-tables.md)** — Interactive data analysis
- **[CLI Reference](../reference/cli.md)** — Disk-based CSV extraction
- **[Table Relationships](table-relationships.md)** — How tables relate to each other
- **[Table Schemas](../reference/table-schemas.md)** — Complete field documentation
