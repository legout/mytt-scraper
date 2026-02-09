# Player Search Guide

The scraper now includes player search functionality! This allows you to find players on mytischtennis.de and then fetch their detailed data.

## Quick Start

```bash
python mytischtennis_scraper.py
```

Select mode 4 or 5 for searching.

## Search Modes

### Mode 4: Search for Players (Interactive)

Search for players and optionally fetch their data:

```
Mode [1-5]: 4

Enter search query (or 'q' to quit): Müller

Search method:
  1. API search (fast)
  2. Playwright search (reliable, shows page)

Select method [1/2]: 1
```

**Features:**
- Interactive search loop - search as many players as you want
- View results with name, club, TTR, and user-id
- Option to fetch detailed data for any found player
- Results saved to `tables/search_*.csv`

### Mode 5: Search and Fetch (Batch)

Search once, select multiple players, and fetch all their data:

```
Mode [1-5]: 5

Enter search query: Müller

Search method:
  1. API search
  2. Playwright search

Select method [1/2]: 1

Select players to fetch (comma-separated numbers, or 'all'):
1,3,5
```

**Features:**
- Search once and see all results
- Select multiple players to fetch
- Use 'all' to fetch everyone
- Each player's data saved with unique prefix

## Search Methods

### API Search (Method 1)

**Pros:**
- Fast
- No browser window
- Returns JSON data directly

**Cons:**
- May not find all players
- Limited to available endpoints

**Use when:** Quick searches, you know the player exists

### Playwright Search (Method 2)

**Pros:**
- Uses actual website search UI
- More comprehensive results
- Shows what the site finds

**Cons:**
- Opens browser window (unless headless)
- Slower than API

**Use when:** You can't find a player via API, want to see page results

## Search Results

When you search, you'll see:

```
5 player(s) found:

1. Thomas Müller
   Club: TSV Güntersleben
   TTR: 1579
   User-ID: 2fa35076-e634-457c-bf70-e89a70e0b7b0

2. Anna Schmidt
   Club: TTC Würzburg
   TTR: 1420
   User-ID: 5c8f3a1b-...
```

You can then:
- Enter a number to fetch that player's data
- Type 'n' to continue searching
- Copy the user-id for future use

## Use Cases

### Find Opponents

```bash
# Search for opponent
Mode [1-5]: 4
Enter search query: Buchinger

# Results show with their TTR
# Fetch their data to see match history
Fetch data for a player? (enter number or 'n'): 1
```

### Team Player Search

Search for all players from a club:

```bash
Mode [1-5]: 4
Enter search query: TSV Güntersleben
```

Then fetch multiple team members using mode 5!

### Batch Scouting

Search and fetch multiple opponents at once:

```bash
Mode [1-5]: 5
Enter search query: Versbach

# Select all opponents
Selection: all

# Fetches all players from the search results
```

## Search Tips

### Query Types

- **Player names:** `Thomas Müller`, `Schmidt`, etc.
- **Clubs:** `TSV Güntersleben`, `TTC Würzburg`, etc.
- **TTR ranges:** Some searches might support this

### Best Practices

1. **Use partial names:** If unsure of spelling, use partial:
   - `Müller` instead of `Thomas Müller`
   - `Schmidt` instead of `Anna Maria Schmidt`

2. **Try both methods:** If API search fails, try Playwright

3. **Save user-ids:** Once you find a player, save their user-id for:
   - Quick future fetching
   - Adding to batch lists

4. **Use club names:** Searching by club often finds all members

## Search Results Files

Search results are saved as CSV files:

```
search_Müller_20250207_123045.csv
search_Versbach_20250207_123100.csv
```

**Columns:**
- `user_id` - Player's unique ID
- `name` - Player name
- `firstname`, `lastname` - Split name
- `club` - Club name
- `ttr` - Current TTR
- `personId` - Alternative ID field

## Integration with Data Fetching

After finding players, you can:

### 1. Fetch Individual Player
```bash
# From search mode
Fetch data for a player? (enter number or 'n'): 1

# Fetches all tables:
# - player_x_club_info.csv
# - player_x_ttr_rankings.csv
# - player_x_ttr_history_events.csv
# - player_x_ttr_history_matches.csv
```

### 2. Batch Fetch with User-IDs
```bash
# Save user-ids to a file
echo "id1,id2,id3" > user_ids.txt

# Then use mode 3 with the file
python mytischtennis_scraper.py
Mode [1-5]: 3
Enter file with search queries: user_ids.txt
```

### 3. Use Standalone Script

```bash
python player_search.py

# Select mode 1 for interactive search
# Search and fetch players in one workflow
```

## Examples

### Compare Opponent TTR History

```bash
# 1. Search for opponent
Mode [1-5]: 4
Enter search query: Buchinger

# 2. Fetch their data
Fetch data for a player? (enter number or 'n'): 1

# 3. Analyze with pandas
python analyze_tables.py
```

### Scout Team Before Match

```bash
# Search for entire team
Mode [1-5]: 4
Enter search query: TSV 1876 Thüngersheim

# Fetch all members
Selection: all

# Get all their data for pre-match analysis!
```

## Troubleshooting

### No Players Found

1. **Try partial names:** Use shorter versions
2. **Switch method:** API → Playwright or vice versa
3. **Check spelling:** German special characters (ü, ö, ä, ß)

### Can't Fetch Player

If search finds a player but fetch fails:
1. Check if user-id is correct
2. Verify you're logged in
3. Run in headed mode to see errors

### Playwright Search Issues

- Make sure you're logged in first
- If browser opens but doesn't find search, the site may have changed
- Try using the search in a regular browser first

## Advanced Usage

### Programmatic Search

```python
from mytischtennis_scraper import MyTischtennisScraper

scraper = MyTischtennisScraper("email", "password", headless=True)
scraper.login()

# Search
results = scraper.search_players("Müller", use_playwright=False)

# Process results
for player in results:
    user_id = player.get('user_id')
    if user_id:
        data = scraper.run_external_profile(user_id)
```

### Search and Analyze

```python
import pandas as pd

# Search results
search_results = pd.read_csv('tables/search_Müller_*.csv')

# Compare multiple opponents
for _, row in search_results.iterrows():
    user_id = row['user_id']
    # Load their TTR history
    history_file = f'tables/{user_id}_ttr_history_events.csv'
    history = pd.read_csv(history_file)

    # Analyze their performance
    ttr_change = history['ttr_delta'].sum()
    print(f"{row['name']}: TTR change {ttr_change:+}")
```

## Summary

The player search feature lets you:
- ✅ Find players by name or club
- ✅ See their TTR rating instantly
- ✅ Get their user-id for detailed fetching
- ✅ Batch fetch multiple opponents
- ✅ Scout teams before matches
- ✅ Save search results for later use

Combined with the existing data fetching, you now have a complete tool for exploring and analyzing mytischtennis.de player data!
