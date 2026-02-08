# How to Fetch an External Profile

Download detailed data for a specific player using their user ID. This guide covers both CLI and TUI approaches.

## What You'll Learn

- Find a player's user ID
- Fetch profile data by user ID
- Understand the output files
- Save data with custom prefixes

---

## Prerequisites

- You have [completed your first run](../tutorials/first-run.md) (installed dependencies and logged in at least once)
- You have a valid user ID for the player you want to fetch

**Don't have a user ID?** See [How to Search for Players](search-players.md) to find players and their IDs.

---

## Finding User IDs

Before fetching external profiles, you need the player's user ID. Here are three ways to find it:

### Method 1: From Search Results

After searching (see [Search for Players](search-players.md)), the User-ID column shows the identifier:

```
1. Thomas Müller
   Club: TSV Güntersleben
   TTR: 1579
   User-ID: 2fa35076-e634-457c-bf70-e89a70e0b7b0
```

### Method 2: From the Website

When viewing a player's profile on mytischtennis.de, the user ID is in the URL:

```
https://www.mytischtennis.de/community/external-profile?user-id=2fa35076-e634-457c-bf70-e89a70e0b7b0
                                                            └──────────────────────────────────┘
                                                                        User ID
```

### Method 3: From Saved Search CSV

Previous search results are saved to `tables/search_*.csv`:

```csv
user_id,name,club,ttr
2fa35076-e634-457c-bf70-e89a70e0b7b0,Thomas Müller,TSV Güntersleben,1579
```

---

## Method 1: Using the CLI

The CLI provides a straightforward prompt-based workflow.

### Basic Fetch

```bash
python scripts/main.py
```

At the mode selection prompt, choose option 2:

```
Select mode:
  1. Own profile
  2. External profile (by user-id)
  3. Multiple profiles (from file)
  4. Search for players
  5. Search and fetch (batch)

Mode [1-5]: 2
```

Enter the user ID when prompted:

```
Enter user-id: 2fa35076-e634-457c-bf70-e89a70e0b7b0
```

Optionally add a file prefix:

```
Enter file prefix (optional, press Enter to use user-id): opponent_müller
```

**Without prefix:** Files are named `2fa35076-e634-457c-bf70-e89a70e0b7b0_*.csv`

**With prefix:** Files are named `opponent_müller_*.csv`

### What Happens Next

The scraper:
1. Logs in to mytischtennis.de (if not already logged in)
2. Fetches the external profile data
3. Extracts and saves tables to CSV files

You'll see progress output:

```
Fetching: External profile (user-id: 2fa35076-e634-457c-bf70-e89a70e0b7b0)
URL: https://www.mytischtennis.de/community/external-profile?user-id=...
Response status: 200
✓ Successfully fetched and parsed data

============================================================
Extracting tables (prefix: opponent_müller_)
============================================================

✓ All tables extracted

============================================================
✓ All tables extracted
============================================================
```

---

## Method 2: Using the TUI

The TUI provides a visual modal dialog for entering user IDs with background progress tracking.

### Starting the TUI

```bash
python -m mytt_scraper.tui
```

### Step 1: Log In

Enter your credentials on the login screen and press **Login**.

### Step 2: Open the User ID Dialog

From the main menu, select **Fetch by User ID**.

### Step 3: Enter the User ID

A modal dialog appears:

```
┌────────────────────────────────────────────┐
│           Enter User ID                    │
├────────────────────────────────────────────┤
│  [2fa35076-e634-457c-bf70-e89a70e0b7b0]   │
│                                            │
│      [ Cancel ]    [ Fetch ]               │
└────────────────────────────────────────────┘
```

Paste or type the user ID and click **Fetch** (or press **Enter**).

### Step 4: Monitor Progress

The main menu shows a status message during the fetch:

```
┌────────────────────────────────────────────┐
│  Main Menu                                 │
├────────────────────────────────────────────┤
│  🔄 Fetching profile for user:             │
│     2fa35076-e634-457c-bf70...            │
│                                            │
│     [ Fetch My Profile ]                   │
│     [ Search Players ]                     │
│     [ Fetch by User ID ]                   │
└────────────────────────────────────────────┘
```

The fetch runs in a background worker, so the UI remains responsive.

### Step 5: Review Results

When complete, a results modal appears:

```
┌────────────────────────────────────────────┐
│           Fetch Results                    │
├────────────────────────────────────────────┤
│  ✓ Successfully fetched profile for:       │
│     2fa35076-e634-457c-bf70-e89a70e0b7b0  │
│                                            │
│  Tables directory: tables                  │
│                                            │
│  Files written (5):                        │
│    • 2fa35076-e634-457c-bf70..._club_info.csv
│    • 2fa35076-e634-457c-bf70..._ttr_rankings.csv
│    • 2fa35076-e634-457c-bf70..._league_table.csv
│    • 2fa35076-e634-457c-bf70..._ttr_history_events.csv
│    • 2fa35076-e634-457c-bf70..._ttr_history_matches.csv
│                                            │
│            [ Close ]                       │
└────────────────────────────────────────────┘
```

Click **Close** (or press **Q** or **Escape**) to return to the main menu.

---

## Understanding the Output Files

Each external profile fetch creates five CSV files in the `tables/` directory:

### 1. Club Info (`{prefix}_club_info.csv`)

```csv
clubNr,association,season,group_name,group_name_short,group_id,extracted_at
12345,ByTTV,2024/25,Bezirksklasse Würzburg Gruppe 1,BK Würzburg 1,abc123,2025-02-07T12:30:45
```

**Use for:** Understanding which club and league the player belongs to.

### 2. TTR Rankings (`{prefix}_ttr_rankings.csv`)

```csv
position,firstname,lastname,rank,germanRank,clubSexRank,germanSexRank,fedRank,matchCount,clubName,personId
5,Thomas,Müller,1579,45231,3,15234,892,42,TSV Güntersleben,abc123
```

**Use for:** Comparing TTR ratings, match counts, and rankings.

### 3. League Table (`{prefix}_league_table.csv`)

```csv
season,league,group_id,table_rank,teamname,own_points,other_points,tendency
2024/25,Bezirksklasse Würzburg,abc123,3,TSV Güntersleben,12:4,steady
```

**Use for:** Seeing the player's team position in the league.

### 4. TTR History Events (`{prefix}_ttr_history_events.csv`)

```csv
event_date_time,formattedEventDate,event_name,event_id,type,ttr_before,ttr_after,ttr_delta,match_count,matches_won,matches_lost
2025-01-15T19:00:00,15.01.2025,Heimspiel gegen TTC Würzburg,evt123,competition,1575,1579,+4,5,3,2
```

**Use for:** Analyzing TTR progression over time, identifying strong/weak periods.

### 5. TTR History Matches (`{prefix}_ttr_history_matches.csv`)

```csv
event_id,event_name,match_number,own_person_name,other_person_name,other_ttr,own_set1,other_set1,own_set2,other_set2,...
evt123,Heimspiel gegen TTC Würzburg,1,Thomas Müller,Max Mustermann,1620,11,9,11,7,11,5,,,,,2,0,33,21
```

**Use for:** Detailed match analysis, set scores, opponent strengths.

---

## Using Custom Prefixes

Prefixes help organize files when fetching multiple players.

### CLI Example

```
Enter file prefix (optional): opponent_müller
# Creates: opponent_müller_*.csv

Enter file prefix (optional): teammate_anna
# Creates: teammate_anna_*.csv
```

### Why Use Prefixes?

Without prefixes, files are named with the full user ID:

```
tables/
├── 2fa35076-e634-457c-bf70-e89a70e0b7b0_club_info.csv
├── 2fa35076-e634-457c-bf70-e89a70e0b7b0_ttr_rankings.csv
├── a1b2c3d4-e5f6-7890-abcd-ef1234567890_club_info.csv
└── a1b2c3d4-e5f6-7890-abcd-ef1234567890_ttr_rankings.csv
```

With prefixes, files are human-readable:

```
tables/
├── opponent_müller_club_info.csv
├── opponent_müller_ttr_rankings.csv
├── teammate_anna_club_info.csv
└── teammate_anna_ttr_rankings.csv
```

---

## Viewing Fetched Data

### Option 1: Using the TUI Table Viewer

If you fetched data using the TUI, click **View Tables** from the main menu to browse all fetched tables with filtering and sorting.

### Option 2: Command Line

Use your preferred CSV viewer:

```bash
# View with column alignment
 column -s, -t < tables/opponent_müller_ttr_rankings.csv | less -S

# Count rows
wc -l tables/opponent_müller_*.csv

# Quick preview (first 10 lines)
head tables/opponent_müller_ttr_history_events.csv
```

### Option 3: Spreadsheet Applications

Open CSV files directly in:
- Excel
- Google Sheets
- LibreOffice Calc
- Numbers (macOS)

---

## Tips and Best Practices

### Organizing Multiple Fetches

Create a naming convention for prefixes:

```
# Opponents (scouting)
opponent_{lastname}_{date}
# Example: opponent_müller_20250207

# Teammates
teammate_{firstname}
# Example: teammate_thomas

# Tournaments
tournament_{name}_{date}
# Example: tournament_citycup_20250207
```

### Batch Fetching Multiple Profiles

For fetching many profiles at once, use mode 3 with a file:

```bash
# Create a file with user IDs
echo "id1,id2,id3" > user_ids.txt

# Run in mode 3
python scripts/main.py
Mode [1-5]: 3
Enter file with search queries: user_ids.txt
```

See [Fetch Multiple Players](fetch-multiple.md) for details.

### Checking Data Freshness

The `extracted_at` column in club_info.csv shows when data was fetched:

```csv
extracted_at
2025-02-07T12:30:45
```

Re-fetch if the data is stale (TTR ratings change frequently).

---

## Troubleshooting

### "Failed to fetch profile data"

1. **Check the user ID**: Ensure it's a complete UUID format (36 characters with hyphens)
2. **Verify login**: Run a test fetch of your own profile first
3. **Try headed mode**: Some profiles may require visible browser interaction

### Files Not Created

Check that the `tables/` directory exists and is writable:

```bash
ls -la tables/
mkdir -p tables
```

### Empty Tables

Some players may have privacy settings that limit data visibility:
- TTR history may be empty
- League data may not be available
- Club info should always be present if the profile exists

---

## Related Guides

- [Search for Players](search-players.md) - Find players and their user IDs
- [Fetch Multiple Players](fetch-multiple.md) - Batch operations from a file
- [Filter and Query Tables](filter-query-tables.md) - Analyze fetched data with the TUI
- [Tutorial: First Run](../tutorials/first-run.md) - Installation and setup
