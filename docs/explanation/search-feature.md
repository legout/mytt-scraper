# Player Search Feature - Summary

## What's New

The scraper now includes **player search functionality** that allows you to:
- Find players by name or club
- See their TTR rating instantly
- Get their user-id for detailed data fetching
- Batch fetch multiple opponents
- Scout teams before matches

## New Modes

| Mode | Description | New? |
|-------|-------------|--------|
| 1 | Own profile | No |
| 2 | External profile | No |
| 3 | Multiple profiles | No |
| 4 | Search players | ✨ **NEW** |
| 5 | Search & fetch | ✨ **NEW** |

## Files Created

| File | Purpose |
|------|----------|
| `player_search.py` | Standalone search script with full-featured search UI |
| `example_search.py` | Quick example: search and fetch one player |
| `SEARCH_GUIDE.md` | Complete guide for all search features |
| `mytischtennis_scraper.py` | **Updated** - integrated PlayerSearcher mixin |
| `README.md` | **Updated** - added search modes to documentation |

## Search Functionality

### Search Methods

1. **API Search** (Fast)
   - Direct API requests
   - No browser needed
   - Quick results

2. **Playwright Search** (Reliable)
   - Uses actual website search UI
   - More comprehensive results
   - Shows page behavior

### Search Results

Each result includes:
- **Name** - Player name
- **Club** - Club affiliation
- **TTR** - Current rating
- **User-ID** - Unique identifier for fetching

### Integration with Data Fetching

After searching, you can:
- Fetch individual player's detailed data
- Batch fetch multiple players
- Compare opponents' TTR history
- Scout entire teams

## Use Cases

### 1. Find and Scout Opponent
```bash
python mytischtennis_scraper.py
# Mode 4
Enter search query: Buchinger
# See their TTR immediately
# Fetch their full data if needed
```

### 2. Scout Team
```bash
# Search for club
Enter search query: TSV Güntersleben
# Get all team members
# Use mode 5 to fetch everyone
```

### 3. Batch Opponent Analysis
```bash
# Search and fetch multiple opponents at once
Mode [1-5]: 5
Enter search query: Versbach
Selection: all
# Get all their TTR histories!
```

## Search Workflows

### Interactive Search Loop (Mode 4)

```
1. Enter search query
2. View results
3. Optionally fetch a player's data
4. Repeat with new query
```

### Batch Search and Fetch (Mode 5)

```
1. Enter search query
2. View all results
3. Select multiple players (numbers or 'all')
4. Fetch all selected players' data
```

### Programmatic Search

```python
from mytischtennis_scraper import MyTischtennisScraper

scraper = MyTischtennisScraper("email", "password")
scraper.login()

# Search
results = scraper.search_players("Müller")

# Fetch data for each
for player in results:
    user_id = player['user_id']
    scraper.run_external_profile(user_id)
```

## Example Session

```bash
$ python mytischtennis_scraper.py

Username (email): your@email.com
Password: ********

Select mode:
  1. Own profile
  2. External profile (by user-id)
  3. Multiple profiles
  4. Search for players
  5. Search and fetch

Mode [1-5]: 4

Enter search query: Buchinger

Search method:
  1. API search (fast)
  2. Playwright search (reliable, shows page)

Select method [1/2]: 1
Searching for players: 'Buchinger'
Trying API: Community search
✓ Found 1 player(s) via API

============================================================
 Search Results for 'Buchinger'
============================================================

1 player(s) found:

1. Buchinger, Nils
   Club: TSV Grombühl Würzburg II
   TTR: 1543
   User-ID: NU134102

Fetch data for a player? (enter number or 'n'): 1

Fetching: Buchinger, Nils
✓ Created tables/NU134102_club_info.csv (1 row)
✓ Created tables/NU134102_ttr_rankings.csv (5 rows)
✓ Created tables/NU134102_league_table.csv (5 rows)
✓ Created tables/NU134102_ttr_history_events.csv (123 rows)
✓ Created tables/NU134102_ttr_history_matches.csv (45 rows)
```

## Technical Details

### Implementation

The search functionality uses:
- `PlayerSearcher` mixin class - provides search methods
- API endpoint probing - tries multiple search endpoints
- HTML parsing fallback - extracts player links from page
- Playwright integration - uses browser for UI interaction

### Data Structures

**Search Result:**
```python
{
    'user_id': '2fa35076-e634-457c-bf70-e89a70e0b7b0',
    'name': 'Player Name',
    'club': 'Club Name',
    'ttr': 1543,
    'personId': 'NU123456',
    # ... other fields
}
```

### Search Queries Saved

Search results are automatically saved to `tables/`:
```
search_PlayerName_20250207_123045.csv
```

Columns: user_id, name, firstname, lastname, club, clubNr, ttr, external_id, personId

## Files Updated

### Core Scraper
- ✅ `mytischtennis_scraper.py` - Added PlayerSearcher mixin
  - `search_players(query, use_playwright)` - Main search method
  - `_search_via_api(query)` - API endpoint probing
  - `_search_via_playwright(query)` - Browser-based search
  - `run_search_mode()` - Interactive search (mode 4)
  - `run_search_and_fetch_mode()` - Batch search & fetch (mode 5)

### New Scripts
- ✅ `player_search.py` - Full-featured standalone search script
- ✅ `example_search.py` - Simple search and fetch example

### Documentation
- ✅ `SEARCH_GUIDE.md` - Complete search documentation
- ✅ `README.md` - Updated with search modes

## Quick Start

```bash
# Update dependencies (if needed)
uv sync

# Run scraper with search
python mytischtennis_scraper.py

# Select mode 4 or 5
# Search for players and fetch their data!
```

Or run standalone search:
```bash
python player_search.py
```

## Summary

With the new player search feature, the scraper is now a **complete player exploration tool**:

1. ✅ Find any player by name or club
2. ✅ View their current TTR instantly
3. ✅ Get their user-id for detailed access
4. ✅ Fetch complete data with match history
5. ✅ Batch search and fetch multiple opponents
6. ✅ Scout entire teams at once

Perfect for:
- Preparing for upcoming matches
- Analyzing opponent performance
- Finding new club members
- Recruiting players
- Comparing team statistics

All integrated into one tool with your existing authentication!
