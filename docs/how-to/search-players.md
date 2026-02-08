# How to Search for Players

Find players on mytischtennis.de by name or club. This guide covers both the CLI and TUI approaches.

## What You'll Learn

- Search for players by name or club
- Choose between API and Playwright search methods
- Select and fetch data for multiple players
- Save search results for later use

---

## Prerequisites

- You have [completed your first run](../tutorials/first-run.md) (installed dependencies and logged in at least once)
- Your mytischtennis.de credentials are valid

---

## Method 1: Using the CLI

The CLI provides two search modes: interactive search (mode 4) and batch search-and-fetch (mode 5).

### Option A: Interactive Search (Mode 4)

Best for: Exploring search results and fetching individual players as you go.

```bash
python scripts/main.py
```

At the mode selection prompt:

```
Select mode:
  1. Own profile
  2. External profile (by user-id)
  3. Multiple profiles (from file)
  4. Search for players
  5. Search and fetch (batch)

Mode [1-5]: 4
```

Enter your search query:

```
Enter search query (or 'q' to quit): Müller
```

Choose your search method:

```
Search method:
  1. API search (fast)
  2. Playwright search (reliable, shows page)

Select method [1/2]: 1
```

**Understanding the options:**

| Method | Speed | Best For |
|--------|-------|----------|
| **API search** (1) | Fast | Quick lookups, when you know the player exists |
| **Playwright** (2) | Slower | Comprehensive results, when API search returns nothing |

Review the results:

```
3 player(s) found:

1. Thomas Müller
   Club: TSV Güntersleben
   TTR: 1579
   User-ID: 2fa35076-e634-457c-bf70-e89a70e0b7b0

2. Anna Müller
   Club: TTC Würzburg
   TTR: 1420
   User-ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

To fetch a player's data immediately:

```
Fetch data for a player? (enter number or 'n'): 1
```

This fetches all tables for the selected player. Enter `n` to continue searching with a new query.

### Option B: Batch Search and Fetch (Mode 5)

Best for: Fetching data for multiple players at once (e.g., scouting a team).

```bash
python scripts/main.py
```

Select mode 5:

```
Mode [1-5]: 5
```

Enter your search query and select all matching players:

```
Enter search query: TSV Güntersleben

Select method [1/2]: 2

5 player(s) found:

Select players to fetch (comma-separated numbers, or 'all'): all
```

Or fetch specific players by number:

```
Select players to fetch (comma-separated numbers, or 'all'): 1,3,5
```

The CLI fetches each player's data sequentially with a 1-second delay between requests.

---

## Method 2: Using the TUI

The TUI provides a visual interface with a searchable results table and multi-select capability.

### Starting the TUI

```bash
python -m mytt_scraper.tui
```

### Step 1: Log In

Enter your credentials on the login screen and press **Login** (or press **Enter**).

### Step 2: Open the Search Screen

From the main menu, select **Search Players**.

### Step 3: Configure Search

```
┌─────────────────────────────────────────┐
│  Search Players                         │
├─────────────────────────────────────────┤
│  [Search input field      ]             │
│  Use Playwright: [■] (Playwright mode)  │
│                                         │
│         [ Search ]                      │
└─────────────────────────────────────────┘
```

Toggle **Use Playwright** on or off depending on your needs:
- **Off (API mode)**: Fast search, good for known players
- **On (Playwright mode)**: Opens browser, more comprehensive results

### Step 4: Review Results

Results appear in a scrollable table:

```
┌───┬───────────────┬────────────────────┬──────┬──────────────────────────────┐
│ ✓ │ Name          │ Club               │ TTR  │ User ID                      │
├───┼───────────────┼────────────────────┼──────┼──────────────────────────────┤
│ ☐ │ Thomas Müller │ TSV Güntersleben   │ 1579 │ 2fa35076-e634-457c-bf70-...  │
│ ☐ │ Anna Müller   │ TTC Würzburg       │ 1420 │ a1b2c3d4-e5f6-7890-abcd-...  │
└───┴───────────────┴────────────────────┴──────┴──────────────────────────────┘
```

### Step 5: Select Players

- **Navigate**: Use ↑/↓ arrow keys to move between rows
- **Toggle selection**: Press **Space** or **Enter** to select/deselect a player
- **Select all**: Click **Select All** button
- **Clear selection**: Click **Clear Selection** button

Selected rows show **☑** instead of **☐**.

### Step 6: Fetch Selected Players

Click **Fetch N Players** (the button updates with your selection count).

A progress screen appears showing:
- Progress bar with completion status
- Success/failure counts
- Per-player fetch log

Press **B** (or click **Back to Search**) to return to search results when complete.

---

## Understanding Search Results

### Saved Files

Search results are automatically saved to CSV:

```
tables/search_Müller_20250207_123045.csv
```

**Columns:**
- `user_id` - Player's unique identifier
- `name` - Full name
- `firstname`, `lastname` - Split name fields
- `club` - Club name
- `ttr` - Current TTR rating
- `personId` - Alternative ID field

### Finding User IDs

User IDs appear in two places:
1. **Search results** - In the User-ID column (CLI) or User ID column (TUI)
2. **Profile URLs** - When viewing a player's profile on mytischtennis.de:
   ```
   https://www.mytischtennis.de/community/external-profile?user-id=2fa35076-e634-457c-bf70-e89a70e0b7b0
   ```

Save these IDs for quick future fetching without searching again.

---

## Tips and Best Practices

### Search Query Tips

- **Partial names work**: `Müller` finds more results than `Thomas Müller`
- **Club searches**: Enter a club name to find all members
- **Special characters**: German characters (ä, ö, ü, ß) are supported

### When to Use Each Method

**Use API search when:**
- You need results quickly
- You've searched for this player before
- You're iterating through multiple queries

**Use Playwright search when:**
- API search returns no results
- You need the most comprehensive results
- You're searching by club name

### Common Workflows

**Scout an opponent:**
1. Search for the player's name
2. Note their TTR and club
3. Fetch their data to analyze match history

**Prepare for a team match:**
1. Search by opposing team name
2. Select all players
3. Batch fetch for offline analysis

---

## Troubleshooting

### No Players Found

1. **Try a partial name**: Use `Müll` instead of `Müller, Thomas`
2. **Switch methods**: If API fails, try Playwright (and vice versa)
3. **Check spelling**: Verify special characters and umlauts

### Cannot Fetch Player

- Ensure you selected the player (TUI: checkbox shows ☑)
- Check that you have an active internet connection
- Verify you're still logged in (re-run login if needed)

---

## Related Guides

- [Fetch by User ID](fetch-by-user-id.md) - Skip searching and fetch directly with an ID
- [Fetch Multiple Players](fetch-multiple.md) - Batch operations from a file
- [Tutorial: First Run](../tutorials/first-run.md) - Installation and setup
