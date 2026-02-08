# CLI Reference

Complete reference for the `mytt-scraper` command-line interface.

## Synopsis

```bash
mytt-scraper
```

The CLI runs interactively and prompts for all required information.

## Global Prompts

When you run `mytt-scraper`, you'll be prompted for:

### Authentication

| Prompt | Description | Required |
|--------|-------------|----------|
| `Username (email)` | Your mytischtennis.de login email | Yes |
| `Password` | Your mytischtennis.de password | Yes |

### Mode Selection

| Prompt | Options | Description |
|--------|---------|-------------|
| `Mode [1-5]` | `1` - Own profile | Fetch your own community data |
| | `2` - External profile | Fetch data for a specific player by user-id |
| | `3` - Multiple profiles | Batch fetch data for multiple players |
| | `4` - Search for players | Search and find players by name or club |
| | `5` - Search and fetch | Search for players and fetch their data |

### Browser Mode

| Prompt | Options | Default | Description |
|--------|---------|---------|-------------|
| `Run in headed mode?` | `y` / `N` | `N` (headless) | Show browser window during scraping |

**Headed mode** (`y`): Visible browser window, useful for debugging login issues or captchas.

**Headless mode** (`N`): Browser runs in background, faster and less intrusive.

---

## Mode 1: Own Profile

Fetch your own community data including TTR rankings, league tables, and match history.

### Additional Prompts

None. After selecting mode `1`, the scraper proceeds automatically.

### Output Files

All files are saved to the `tables/` directory (created automatically):

| File | Description |
|------|-------------|
| `club_info.csv` | Your club information and league details |
| `ttr_rankings.csv` | TTR rankings for your club |
| `league_table.csv` | Current league standings |
| `ttr_history_events.csv` | Your TTR history events |
| `ttr_history_matches.csv` | Individual matches from TTR events |

### Example Session

```
=== MyTischtennis.de Scraper ===

Username (email): user@example.com
Password: ********

Select mode:
  1. Own profile
  2. External profile (by user-id)
  3. Multiple profiles
  4. Search for players
  5. Search and fetch

Mode [1-5]: 1

Run in headed mode? (shows browser window) [y/N]: N

Fetching: Own community data
URL: https://www.mytischtennis.de/community?show=everything&_data=routes%2F%24
tables/club_info.csv: 1 rows x 8 columns
...
✓ All tables extracted

✓ Own profile data extracted!
```

---

## Mode 2: External Profile

Fetch data for a specific player using their user-id.

### Additional Prompts

| Prompt | Description | Required |
|--------|-------------|----------|
| `Enter user-id` | The player's user-id (UUID format) | Yes |
| `Enter file prefix` | Optional prefix for output files | No |

### Finding User-IDs

User-ids can be found in URLs when viewing player profiles:

```
https://www.mytischtennis.de/community/external-profile?user-id=2fa35076-e634-457c-bf70-e89a70e0b7b0
                                                         └──────────────────────────────────────┘
                                                                     User-ID
```

### Output Files

Files are prefixed with the user-id (or your custom prefix):

| File Pattern | Description |
|--------------|-------------|
| `{user-id}_club_info.csv` | Player's club information |
| `{user-id}_ttr_rankings.csv` | Player's TTR rankings |
| `{user-id}_league_table.csv` | Player's league standings |
| `{user-id}_ttr_history_events.csv` | Player's TTR history events |
| `{user-id}_ttr_history_matches.csv` | Player's individual matches |

### Example Session

```
Mode [1-5]: 2
Enter user-id: 2fa35076-e634-457c-bf70-e89a70e0b7b0
Enter file prefix (optional, press Enter to use user-id): 

Fetching: External profile (user-id: 2fa35076-e634-457c-bf70-e89a70e0b7b0)
...
✓ External profile data extracted for 2fa35076-e634-457c-bf70-e89a70e0b7b0!
```

---

## Mode 3: Multiple Profiles

Batch fetch data for multiple players in a single session.

### Additional Prompts

| Prompt | Description | Format |
|--------|-------------|--------|
| `Enter user-ids` | Comma-separated list of user-ids | `id1,id2,id3` |

### Output Files

Each player's data is saved with their user-id as prefix:

```
tables/
├── {user-id-1}_club_info.csv
├── {user-id-1}_ttr_rankings.csv
├── {user-id-2}_club_info.csv
├── {user-id-2}_ttr_rankings.csv
└── ...
```

### Behavior

- Profiles are processed sequentially with a 1-second delay between requests
- If one profile fails, the scraper continues with the next
- Progress is displayed: `Processing profile 1/3: {user-id}`

### Example Session

```
Mode [1-5]: 3
Enter user-ids (comma-separated): 2fa35076-e634-457c-bf70-e89a70e0b7b0,a1b2c3d4-e5f6-7890-abcd-ef1234567890

============================================================
Processing profile 1/2: 2fa35076-e634-457c-bf70-e89a70e0b7b0
============================================================
...

============================================================
Processing profile 2/2: a1b2c3d4-e5f6-7890-abcd-ef1234567890
============================================================
...

✓ Data extracted for 2 profiles!
```

---

## Mode 4: Search for Players

Interactive search to find players by name, club, or other criteria.

### Additional Prompts

| Prompt | Description | Options |
|--------|-------------|---------|
| `Enter search query` | Search term (player name, club, etc.) | Any text |
| `Select method` | Search method | `1` = API, `2` = Playwright |

**API Search (`1`)**: Fast, uses HTTP requests directly.

**Playwright Search (`2`)**: More reliable for complex searches, uses browser automation.

### Interactive Loop

After each search:

| Prompt | Description |
|--------|-------------|
| `Fetch data for a player?` | Enter result number to fetch, or `n` to skip |

Enter `q` at the search query prompt to exit search mode.

### Output Files

| File Pattern | Description |
|--------------|-------------|
| `search_{query}_{timestamp}.csv` | Search results with player details |
| `{user-id}_*.csv` | If you choose to fetch a player's data |

### Search Results Display

```
============================================================
 Search Results for 'Müller'
============================================================

3 player(s) found:

1. Thomas Müller
   Club: TTC Berlin
   TTR: 1650
   User-ID: 2fa35076-e634-457c-bf70-e89a70e0b7b0

2. Anna Müller
   Club: SV Hamburg
   TTR: 1420
   User-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

...

✓ Saved results to tables/search_Müller_20250208_143022.csv
```

### Example Session

```
Mode [1-5]: 4

============================================================
 Player Search Mode
============================================================

Enter search query (or 'q' to quit): Müller

Search method:
  1. API search (fast)
  2. Playwright search (reliable, shows page)

Select method [1/2]: 1
Using API search

Searching for players: 'Müller'
✓ Found 3 player(s) via API
...

Fetch data for a player? (enter number or 'n'): 1

Fetching data for: Thomas Müller
...

Enter search query (or 'q' to quit): q
Exiting search mode...
```

---

## Mode 5: Search and Fetch

Search for players and fetch data for selected results in one operation.

### Additional Prompts

| Prompt | Description | Options |
|--------|-------------|---------|
| `Enter search query` | Search term | Any text |
| `Select method` | Search method | `1` = API, `2` = Playwright |
| `Selection` | Which results to fetch | `all` or comma-separated numbers |

### Selection Options

- **`all`**: Fetch data for all search results
- **`1,3,5`**: Fetch only results 1, 3, and 5
- **`2`**: Fetch only result 2

### Output Files

| File Pattern | Description |
|--------------|-------------|
| `search_{query}_{timestamp}.csv` | Search results |
| `search_{index}_*.csv` | Fetched player data (prefixed with search index) |

### Example Session

```
Mode [1-5]: 5

============================================================
 Search and Fetch Mode
============================================================

Enter search query: TTC München

Search method:
  1. API search
  2. Playwright search

Select method [1/2]: 2

Searching for players: 'TTC München'
✓ Found 5 player(s) via Playwright
...

------------------------------------------------------------
 Select players to fetch (comma-separated numbers, or 'all'):

Selection: 1,2,3

Fetching 3 player(s)...

[1/3] Fetching: Max Mustermann
...
[2/3] Fetching: Erika Musterfrau
...
[3/3] Fetching: Hans Beispiel
...

============================================================
✓ Completed fetching 3 player(s)
============================================================
```

---

## Output Directory Structure

All output is organized in the `tables/` directory:

```
mytt-scraper/
├── tables/
│   ├── club_info.csv                    # Mode 1 (own profile)
│   ├── ttr_rankings.csv
│   ├── league_table.csv
│   ├── ttr_history_events.csv
│   ├── ttr_history_matches.csv
│   │
│   ├── {user-id}_club_info.csv          # Mode 2/3 (external profiles)
│   ├── {user-id}_ttr_rankings.csv
│   │
│   ├── search_Müller_20250208_143022.csv  # Mode 4/5 (search results)
│   ├── search_0_club_info.csv             # Mode 5 (fetched from search)
│   └── search_1_ttr_rankings.csv
```

The output directory can be customized when using the Python API; the CLI always uses `tables/`.

---

## Exit Codes

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success |
| `1` | Error (invalid credentials, network failure, etc.) |

---

## Environment Variables

The CLI does not use environment variables directly. All configuration is provided through interactive prompts. For programmatic usage with environment variables, use the [Python API](python-api.md).

---

## See Also

- [Python API Reference](python-api.md) — Programmatic usage
- [How-To: Search for Players](../how-to/search-players.md) — Step-by-step search guide
- [How-To: Fetch External Profile](../how-to/fetch-external-profile.md) — Detailed profile fetching guide
- [Table Schemas](table-schemas.md) — Complete CSV output documentation