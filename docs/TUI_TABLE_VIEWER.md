# TUI Table Viewer Guide

The mytt-scraper TUI includes a built-in **Table Viewer** that lets you inspect fetched data directly in the terminal—no need to open external tools like Excel or write Python scripts.

## Overview

After fetching profile data through the TUI, you can browse and query extracted tables:

- **TTR Rankings** - Club rankings with TTR ratings
- **League Tables** - League standings and team positions
- **TTR History** - Event history with match details
- **Club Info** - Associated club information

The viewer supports a **dual-source architecture** that prioritizes fresh in-memory data while seamlessly falling back to saved CSV files.

## Accessing the Table Viewer

### Opening "View Tables"

1. Fetch data using any method:
   - **Fetch My Profile** - Your own community data
   - **Search Players** → **Fetch Selected** - Multiple player profiles
   - **Fetch by User ID** - Specific player by ID

2. Once fetch completes, the **"View Tables"** button becomes enabled in the Main Menu

3. Click **"View Tables"** (or navigate to it and press Enter)

```
┌─────────────────────────────────────┐
│  Main Menu                          │
├─────────────────────────────────────┤
│                                     │
│  [Fetch My Profile]                 │
│  [Search Players]                   │
│  [Fetch by User ID]                 │
│  [View Tables]          ← Enabled   │
│                                     │
└─────────────────────────────────────┘
```

### Selecting a Table

The **Table List** screen shows all available tables with source indicators:

```
┌─────────────────────────────────────┐
│  View Tables                        │
├─────────────────────────────────────┤
│  🟢 In-memory  🔵 On disk           │
│                                     │
│  [🟢 TTR Rankings (45 rows)]        │
│  [🟢 League Table (10 rows)]        │
│  [🔵 abc123 - TTR Rankings (38)]    │
│  [🔵 abc123 - League Table (10)]    │
│                                     │
│  [Back to Main Menu]                │
└─────────────────────────────────────┘
```

**Source indicators:**
- 🟢 **Green** - In-memory table (current session, most recent data)
- 🔵 **Blue** - On-disk table (loaded from CSV file)

Click any table to open it in the **Table Preview** screen.

## Dual-Source Data Architecture

The Table Viewer uses a **memory-first, disk-fallback** approach for maximum flexibility:

### 1. In-Memory Tables (Primary Source)

When you fetch data during the current TUI session:

- Tables are extracted and stored as **Polars DataFrames** in memory
- These represent the **most recent** data you've fetched
- Displayed with 🟢 (green indicator)
- Faster access—no file I/O required

**Best for:** Exploring data immediately after fetching

### 2. Disk-Based Tables (Fallback Source)

Tables are also saved as **CSV files** in the `tables/` directory:

- Loaded on-demand when you open the viewer
- Displayed with 🔵 (blue indicator)
- Persisted between TUI sessions
- Can view tables from previous runs without re-fetching

**Best for:** Reviewing historical data from previous sessions

### Source Priority

If a table exists in **both** memory and on disk:

1. **In-memory version is shown** (green indicator)
2. Disk version is hidden to avoid duplicates
3. This ensures you always see the freshest data

### How Data Flows

```
Fetch Profile → Extract Tables → In-Memory (Polars DF)
                                     ↓
                              Save to CSV
                                     ↓
                           View Tables Screen
                            /              \
                     Memory First        Disk Fallback
                    (🟢 green)           (🔵 blue)
```

## Row Cap and Performance

### Default Row Limit

The Table Viewer caps previews at **200 rows** by default:

```
✓ Showing 200 of 1,247 rows
```

### Why the Limit?

1. **UI Responsiveness** - Terminal rendering slows with very large tables
2. **Memory Efficiency** - Prevents loading massive datasets unnecessarily
3. **Lazy Loading** - Disk tables use Polars lazy evaluation:
   ```python
   # Only loads first 200 rows, not entire file
   pl.scan_csv(path).head(200).collect()
   ```

### Row Count Display

The status bar shows both displayed and total rows:

| Status | Meaning |
|--------|---------|
| `✓ Showing 200 of 500 rows` | Capped view (300 rows hidden) |
| `✓ Showing 45 of 45 rows` | Complete view (all rows shown) |

### Working with Large Tables

If your data exceeds the row cap:

1. **Use filters** - Apply filters to reduce results before viewing
2. **Use sorting** - Sort to bring relevant rows to the top
3. **Use aggregations** - Group and summarize instead of viewing raw rows
4. **Use SQL mode** - Write custom queries with `LIMIT` and `OFFSET`

See [TUI Table Queries Guide](TUI_TABLE_QUERIES.md) for advanced querying.

## Supported Table Types

The viewer recognizes these table types with friendly display names:

| Table Type | Display Name | Description |
|------------|--------------|-------------|
| `ttr_rankings` | TTR Rankings | Club TTR rankings with positions |
| `league_table` | League Table | League standings by team |
| `club_info` | Club Info | Club metadata and season info |
| `ttr_history_events` | TTR History Events | Event-level TTR history |
| `ttr_history_matches` | TTR History Matches | Individual match results |
| `tournament_registrations` | Tournament Registrations | Tournament signup data |

### Prefixed Tables

When fetching external profiles, tables are prefixed with the user ID:

```
🟢 abc123 - TTR Rankings (38 rows)
🟢 abc123 - League Table (10 rows)
🔵 xyz789 - TTR Rankings (42 rows)
```

This lets you compare data from multiple players side-by-side.

## Technical Implementation

### Fast Loading with Polars

The Table Viewer uses **Polars** for high-performance data loading:

- **In-memory**: Direct DataFrame operations (zero-copy where possible)
- **Disk**: Lazy CSV scanning with `pl.scan_csv()`
- **Row counting**: Fast line-count without parsing entire files

### Background Workers

Data loading runs in background threads to keep the UI responsive:

```
[Loading ttr_rankings...]  ← Status shows progress
```

You'll see a loading indicator while large CSV files are being scanned.

### PyArrow Support

The viewer also supports **PyArrow Tables** (converted to Polars on display):

```python
# PyArrow Table automatically converted
if hasattr(data, "to_polars"):
    df = data.to_polars()
```

## Keyboard Navigation

| Key | Action |
|-----|--------|
| `↑ / ↓` | Navigate table list or rows |
| `Enter` | Select table / Apply filter |
| `Esc` | Go back |
| `q` | Quit TUI |

In the Table Preview screen:

| Key | Action |
|-----|--------|
| `a` | Apply query/filter |
| `r` | Reset all filters |
| `m` | Toggle Builder/SQL mode |

See [TUI Table Queries Guide](TUI_TABLE_QUERIES.md) for full query controls.

## Troubleshooting

### "View Tables" Button is Disabled

The button is disabled when no tables are available. To enable it:

1. Fetch some data first (any profile)
2. The button activates automatically after successful fetch

### No Tables Listed

If the Table List screen shows "No tables available":

1. Check that the fetch completed successfully
2. Verify the `tables/` directory exists (created automatically on first fetch)
3. Try fetching data again

### Slow Loading

For very large CSV files:

- Loading is limited to 200 rows (fast)
- Use SQL mode with specific filters to reduce data
- Consider fetching less data (specific profiles vs. multiple)

## See Also

- **[TUI Table Queries Guide](TUI_TABLE_QUERIES.md)** - Filtering, sorting, and SQL queries
- **[Usage Guide](USAGE.md)** - Table schemas and data formats
- **[Search Guide](SEARCH_GUIDE.md)** - Finding players to fetch
- **[README.md](../README.md)** - General TUI usage
