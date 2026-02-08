# MyTischtennis.de Scraper

A Python package to login to mytischtennis.de and fetch player data including TTR rankings, league tables, and match history. Uses Playwright for handling JavaScript and captchas automatically.

## Features

- ✅ **Automatic login** with Playwright browser automation
- ✅ **Captcha handling** - automatically clicks checkbox captchas
- ✅ **Multiple modes**:
  - Own profile data
  - External profile (by user-id)
  - Batch fetch for multiple players
  - Player search (NEW!)
  - Search and fetch (NEW!)
- ✅ **Automatic table extraction** - saves data as flat CSV files
- ✅ **Complete history** - TTR changes, match scores, opponents
- ✅ **Player search** - Find opponents by name or club (NEW!)

## Quick Start

### Installation

```bash
# Install dependencies
uv sync

# Install Playwright browser
.venv/bin/playwright install chromium
```

### Basic Usage

```bash
python scripts/main.py
```

You'll be prompted for:
1. Username and password
2. Mode (1-5: own profile, external profile, multiple profiles, search, search & fetch)
3. Whether to run in headed mode (shows browser window)

## Usage Modes

### Mode 1: Own Profile

Fetches your own community data and automatically extracts tables:

```
Username (email): your@email.com
Password: ********
Mode [1-5]: 1
```

**Output files:**
- `tables/club_info.csv` - Club and league information
- `tables/ttr_rankings.csv` - Player rankings
- `tables/league_table.csv` - League standings
- `tables/ttr_history_events.csv` - TTR change history
- `tables/ttr_history_matches.csv` - Detailed match scores

### Mode 2: External Profile

Fetch data for another player using their user-id:

```
Mode [1-5]: 2
Enter user-id: 2fa35076-e634-457c-bf70-e89a70e0b7b0
Enter file prefix (optional): player_x
```

**Output files (with prefix):**
- `tables/player_x_club_info.csv`
- `tables/player_x_ttr_rankings.csv`
- `tables/player_x_league_table.csv`
- `tables/player_x_ttr_history_events.csv`
- `tables/player_x_ttr_history_matches.csv`

**Finding user-ids:**
When viewing another player's profile, the URL contains their user-id:
```
https://www.mytischtennis.de/community/external-profile?user-id=2fa35076-e634-457c-bf70-e89a70e0b7b0
```

### Mode 3: Multiple Profiles

Fetch data for several players at once:

```
Mode [1-5]: 3
Enter user-ids (comma-separated): id1,id2,id3
```

Files are prefixed with each user-id:
- `tables/id1_ttr_rankings.csv`
- `tables/id2_ttr_rankings.csv`
- `tables/id3_ttr_rankings.csv`
- etc.

Perfect for comparing multiple players' data!

### Mode 4: Search for Players (Interactive)

Find opponents or club members by name:

```
Mode [1-5]: 4

Enter search query (or 'q' to quit): Müller

Search method:
  1. API search (fast)
  2. Playwright search (reliable)

Select method [1/2]: 1
```

**Features:**
- Interactive search loop
- View results with name, club, TTR, user-id
- Optionally fetch any player's full data
- Results saved to `tables/search_*.csv`

**See:** [docs/SEARCH_GUIDE.md](docs/SEARCH_GUIDE.md) for detailed search documentation

### Mode 5: Search and Fetch (Batch)

Search once and fetch multiple players:

```
Mode [1-5]: 5
Enter search query: Versbach

Select players to fetch (comma-separated numbers, or 'all'): 1,3,5
```

**Perfect for scouting entire teams or opponent lists!**

## Table Schema

See [docs/USAGE.md](docs/USAGE.md) for detailed table schemas and field descriptions.

## In-Memory Table Extraction (Library Usage)

For library consumers who want to work with data directly without CSV files:

```python
from mytt_scraper import MyTischtennisScraper

scraper = MyTischtennisScraper("your@email.com", "password")
scraper.login()

# Fetch data
data, remaining = scraper.fetch_own_community()

# Extract tables as Polars DataFrames (default)
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# Work with tables in memory
print(tables["ttr_rankings"].head())
print(tables["ttr_history_events"].shape)
```

### Backend Options

Choose your preferred DataFrame backend:

**Polars (default)** - Fast, modern DataFrames:
```python
tables = scraper.extract_flat_tables(data, remaining, backend="polars")
tables["league_table"].filter(pl.col("games") > 5)
```

**Pandas** - Familiar, widely used:
```python
tables = scraper.extract_flat_tables(data, remaining, backend="pandas")
tables["ttr_rankings"].sort_values("ttr", ascending=False)
```

**PyArrow** - Efficient, interoperable:
```python
tables = scraper.extract_flat_tables(data, remaining, backend="pyarrow")
tables["club_info"].to_pandas()  # Convert to pandas if needed
```

### Available Tables

| Table Name | Description |
|------------|-------------|
| `club_info` | Club and league information (single row) |
| `ttr_rankings` | TTR rankings within your club |
| `league_table` | League standings |
| `ttr_history_events` | TTR change events |
| `ttr_history_matches` | Individual match details |

### Missing Table Behavior

Tables are **omitted from the result** when data is not available (e.g., when `remaining` is `None`, history tables are not included). Check for table presence before accessing:

```python
tables = scraper.extract_flat_tables(data, remaining)

if "ttr_history_events" in tables:
    print(f"Found {len(tables['ttr_history_events'])} events")
```

### CSV Extraction Still Available

The in-memory extraction is **additive**—CSV file extraction remains unchanged:

```python
# This still works exactly as before
scraper.extract_and_save_tables(data, remaining, prefix="my_data")
# Creates: tables/my_data_ttr_rankings.csv, etc.
```

## Examples

### Fetch Multiple Players

```python
import sys
from pathlib import Path

# Add src to path
src_dir = Path('src')
sys.path.insert(0, str(src_dir))

from mytt_scraper import MyTischtennisScraper

# Create scraper
scraper = MyTischtennisScraper("your@email.com", "password")

# Login
scraper.login()

# Fetch multiple profiles
user_ids = [
    "2fa35076-e634-457c-bf70-e89a70e0b7b0",
    "another-user-id-here"
]

results = scraper.run_multiple_profiles(user_ids)
```

Or run the example script:
```bash
python scripts/example_fetch_multiple.py
```

### Test with Existing Data

```bash
# Test JSON parsing with existing data
python scripts/test_scraper.py
```

### Search for Players

```bash
python scripts/example_search.py
```

## Project Structure

```
mytt-scraper/
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── .python-version         # Python version
│
├── src/                    # Source code
│   └── mytt_scraper/       # Main package
│       ├── __init__.py
│       ├── config.py       # Configuration constants
│       ├── scraper.py      # Main MyTischtennisScraper class
│       ├── player_search.py # PlayerSearcher class
│       └── utils/          # Utility modules
│           ├── __init__.py
│           ├── auth.py     # Authentication helpers
│           ├── helpers.py  # General utilities
│           └── table_extractor.py # Table extraction logic
│
├── scripts/                # CLI and utility scripts
│   ├── main.py            # Main entry point
│   ├── test_login.py      # Test login
│   ├── test_scraper.py    # Test scraper
│   ├── debug_login.py     # Debug login issues
│   ├── debug_extract.py   # Debug extraction
│   ├── example_fetch_multiple.py
│   └── example_search.py
│
├── docs/                   # Documentation
│   ├── USAGE.md           # Table schemas
│   ├── SEARCH_GUIDE.md    # Search documentation
│   ├── SEARCH_FEATURE.md  # Search feature details
│   ├── COMPLETE_UPDATE.md
│   └── UPDATE_SUMMARY.md
│
├── tests/                  # Tests
│   ├── __init__.py
│   ├── test_scraper.py    # Unit tests
│   └── fixtures/          # Test data
│       └── community_response.json
│
├── examples/               # Example scripts
│   ├── fetch_multiple.py
│   ├── search_players.py
│   ├── analyze_tables.py
│   ├── create_tables.py
│   └── extract_ttr.py
│
├── data/                   # Data storage
│   ├── raw/               # Raw fetched data (JSON)
│   └── processed/         # Processed tables (CSV)
│
└── tables/                 # Output directory for CSV files
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/main.py` | Main entry point with interactive mode selection |
| `scripts/test_scraper.py` | Test JSON parsing with existing data |
| `scripts/test_login.py` | Test login functionality |
| `scripts/debug_login.py` | Debug login issues |
| `scripts/debug_extract.py` | Debug data extraction |
| `scripts/example_fetch_multiple.py` | Example script for fetching multiple players |
| `scripts/example_search.py` | Example script for searching players |
| `examples/analyze_tables.py` | Analyze generated tables with statistics |
| `examples/create_tables.py` | Alternative table creation script |
| `examples/extract_ttr.py` | Extract TTR data from existing JSON |

## Troubleshooting

### Login Issues

Run in **headed mode** to see what's happening:
```
Run in headed mode? (shows browser window) [y/N]: y
```

### Captcha Issues

The script automatically handles checkbox captchas. For complex captchas:
1. Run in headed mode
2. The script will pause before solving
3. You may need to intervene manually

### Rate Limiting

When fetching multiple profiles:
- Script adds 1-second delays between requests
- For large batches, modify `run_multiple_profiles()` delay

## Data Privacy

- Credentials used only for login, never stored
- Cookies extracted from browser session
- No passwords or sensitive data saved to disk
- All fetched data belongs to you/players you query

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/community?show=everything&_data=routes%2F%24` | Own profile data |
| `/community/external-profile?user-id={ID}&show=everything&_data=routes%2F%24` | External profile data |

Both return identical JSON structure with:
- `pageContent.blockLoaderData` - TTR rankings, league table
- Deferred data - TTR history with match details

## Dependencies

- `requests` - HTTP requests after authentication
- `playwright` - Browser automation for login
- `pandas` - Data analysis (optional, for analyze_tables.py)
- `polars` - Data analysis (optional, for analyze_tables.py)
- `duckdb` - Database (optional)

## Development

### Running Tests

```bash
# Run tests
python tests/test_scraper.py

# Or use pytest (when installed)
pytest tests/
```

### Code Organization

The package is structured to be modular and maintainable:
- `config.py` - All configuration constants
- `scraper.py` - Core scraper functionality
- `player_search.py` - Search functionality (extends scraper)
- `utils/auth.py` - Authentication helpers
- `utils/table_extractor.py` - Table extraction logic
- `utils/helpers.py` - General utility functions

## License

For personal use only. Respect mytischtennis.de's terms of service.
