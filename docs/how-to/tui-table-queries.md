# TUI Table Viewer - Filters, Sorting & Queries Guide

The mytt-scraper TUI includes a powerful **Table Preview** screen that allows you to interactively explore fetched data using filters, sorting, and aggregations—without leaving the terminal.

## Overview

When you fetch profile data through the TUI, you can open any table in the **Table Preview** screen to:

- **Filter** rows by column values
- **Sort** by any column (ascending/descending)
- **Group and aggregate** data (count, sum, mean, min, max)
- **Run SQL queries** using DuckDB (advanced mode)

## Opening the Table Preview

The Table Preview screen opens automatically after fetching data, or you can access it when viewing results that include tabular data.

```
┌─────────────────────────────────────────────────────────────────┐
│  Table: ttr_rankings                                            │
├─────────────────────────────────────────────────────────────────┤
│  Mode: [Builder ●]  SQL                                         │
│                                                                 │
│  Filter: [position ▼] [= ▼] [_______]                           │
│  Sort:   [ttr ▼] [Descending ▼]                                 │
│  Group:  [club ▼] [Count ▼]                                     │
│                                                                 │
│  [Apply] [Reset]                                                │
│                                                                 │
│  ✓ Showing 50 of 1,247 rows                                     │
├─────────────────────────────────────────────────────────────────┤
│  │ position │ firstname │ lastname │ ttr  │ club           │   │
│  ├──────────┼───────────┼──────────┼──────┼────────────────┤   │
│  │ 1        │ Max       │ Mustermann│ 1850 │ TSV München    │   │
│  │ 2        │ Anna      │ Schmidt   │ 1823 │ TSV München    │   │
│  ...                                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Query Modes

The Table Preview supports two query modes:

### 1. Builder Mode (Default)

Visual interface for building queries without writing code.

**Controls:**
- **Filter**: Column + Operator + Value
- **Sort**: Column + Direction (Ascending/Descending)
- **Group**: Column + Aggregation function

### 2. SQL Mode (Advanced)

Direct SQL access using DuckDB syntax.

**Example:**
```sql
SELECT club, AVG(ttr) as avg_ttr, COUNT(*) as player_count
FROM data
WHERE ttr > 1500
GROUP BY club
ORDER BY avg_ttr DESC
LIMIT 100
```

Toggle between modes using the **Switch** at the top of the screen or press `m`.

## Filter Operations

### Available Operators

| Operator | Symbol | Description | Example |
|----------|--------|-------------|---------|
| Equals | `=` | Exact match | `club = "TSV München"` |
| Not equals | `≠` | Exclude value | `position ≠ 1` |
| Greater than | `>` | Numeric comparison | `ttr > 1500` |
| Greater or equal | `≥` | Numeric comparison | `ttr ≥ 1600` |
| Less than | `<` | Numeric comparison | `ttr < 2000` |
| Less or equal | `≤` | Numeric comparison | `ttr ≤ 1800` |
| Contains | `contains` | Substring match | `lastname contains "mann"` |

### Type-Aware Filtering

The system automatically converts filter values based on column types:

- **Integer columns** (`int*`): Values parsed as integers
- **Float columns** (`float*`, `double*`): Values parsed as decimals
- **String columns**: Values treated as text (supports `contains`)

**Example:** Filtering `ttr > 1500` on a numeric column will properly compare as numbers, not strings.

## Sorting

Sort by any column in ascending or descending order.

### Multiple Sort Levels

The query system supports multiple sort criteria (applied in order):

1. First sort: `club ASC`
2. Second sort: `ttr DESC`

This groups by club, then sorts by TTR within each club.

## Grouping & Aggregation

Group rows by a column and compute aggregate statistics.

### Available Aggregation Functions

| Function | Description | Use Case |
|----------|-------------|----------|
| **Count** | Number of rows | Count players per club |
| **Sum** | Total of values | Total matches played |
| **Mean** | Average value | Average TTR per club |
| **Min** | Minimum value | Lowest TTR in group |
| **Max** | Maximum value | Highest TTR in group |

### Example: Club Statistics

```
Group: [club ▼] [Mean ▼]
```

Result:
| club | mean_ttr |
|------|----------|
| TSV München | 1723 |
| SC Berlin | 1689 |

### Example: Count Players by Club

```
Group: [club ▼] [Count ▼]
```

Result:
| club | count_club |
|------|------------|
| TSV München | 12 |
| SC Berlin | 8 |

## SQL Query Mode

For complex queries, switch to SQL mode. The Table Preview uses **DuckDB** as the SQL engine.

### SQL Restrictions (Safety)

Only **SELECT** queries are allowed. The following are blocked:
- `INSERT`, `UPDATE`, `DELETE`
- `DROP`, `CREATE`, `ALTER`
- `TRUNCATE`, `MERGE`, `UPSERT`

### SQL Examples

#### Filter and Sort
```sql
SELECT * FROM data
WHERE ttr > 1500 AND club = 'TSV München'
ORDER BY ttr DESC
```

#### Aggregation with GROUP BY
```sql
SELECT 
    club,
    AVG(ttr) as avg_ttr,
    MAX(ttr) as max_ttr,
    COUNT(*) as player_count
FROM data
GROUP BY club
HAVING COUNT(*) > 5
ORDER BY avg_ttr DESC
```

#### String Matching
```sql
SELECT * FROM data
WHERE lastname LIKE '%mann%'
```

#### Numeric Ranges
```sql
SELECT * FROM data
WHERE ttr BETWEEN 1500 AND 1800
```

### Table Name in SQL

When querying in-memory data, the table is always named **`data`**:

```sql
SELECT * FROM data WHERE ...
```

When querying CSV files directly, use the actual filename (without extension).

## Row Cap and Performance

### Default Row Limit

The Table Preview applies a **500-row cap** by default to ensure responsive performance.

```
✓ Showing 500 of 5,247 rows (limit applied)
```

### Why the Limit?

1. **UI Responsiveness**: Large datasets can slow down terminal rendering
2. **Memory Usage**: Prevents loading massive tables into memory
3. **Lazy Evaluation**: Only processed rows are loaded

### Working with Large Tables

If your data exceeds the row cap:

1. **Use filters** to reduce results before viewing
2. **Use aggregations** to summarize instead of viewing raw rows
3. **Use SQL** with `LIMIT` and `OFFSET` for pagination

### Increasing the Limit (SQL Mode)

In SQL mode, you can adjust the limit (up to the max allowed):

```sql
SELECT * FROM data WHERE club = 'TSV München' LIMIT 1000
```

## Backends

The query system supports two execution backends:

### Polars (Default)

- **Used for**: Builder mode queries
- **Features**: Lazy evaluation, fast filtering, expression-based operations
- **Data**: In-memory DataFrames

### DuckDB (SQL Mode)

- **Used for**: SQL queries
- **Features**: Full SQL support, window functions, complex aggregations
- **Data**: In-memory tables and CSV files

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `a` | Apply query |
| `r` | Reset query |
| `m` | Toggle Builder/SQL mode |
| `↑/↓` | Navigate table rows |
| `Esc` | Go back |
| `q` | Quit TUI |

## Common Use Cases

### Find Top-Rated Players

```
Sort: [ttr ▼] [Descending ▼]
[Apply]
```

### Find Players in a Specific Club

```
Filter: [club ▼] [= ▼] [TSV München]
[Apply]
```

### Count Matches Won by Event

```
Group: [event_name ▼] [Sum ▼]
```

(Assumes `matches_won` column exists in the table)

### Find Recent TTR Changes

```sql
SELECT * FROM data
WHERE ttr_delta != 0
ORDER BY event_date_time DESC
LIMIT 50
```

### Calculate Win Rate

```sql
SELECT 
    event_name,
    matches_won * 100.0 / match_count as win_rate
FROM data
WHERE match_count > 0
ORDER BY win_rate DESC
```

## Error Handling

### Validation Errors

If you enter an invalid filter value (e.g., text in a numeric column):

```
❌ Invalid integer: abc
```

### Query Errors

SQL syntax errors are displayed in the status area:

```
❌ SQL error: Binder Error: Referenced column "ttrr" not found
```

### Empty Results

If your query returns no rows:

```
✓ Showing 0 of 1,247 rows
```

Adjust your filters and try again.

## Tips

1. **Start broad, then filter**: Load the table first, then add filters to narrow down
2. **Use Reset often**: The Reset button clears all query parameters and shows the original data
3. **Combine operations**: Filter first, then sort, then group for best performance
4. **Check row counts**: The status bar shows "Showing X of Y rows" to confirm your query scope
5. **Type-aware filtering**: Enter values in the appropriate format for the column type

## See Also

- [Usage Guide](USAGE.md) - Table schemas and data formats
- [Search Guide](SEARCH_GUIDE.md) - Finding players to fetch
- [README.md](../README.md) - General TUI usage
