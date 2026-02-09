# MyTischtennis.de Scraper - Usage Guide

## Features

The scraper now supports three modes:

1. **Own Profile** - Fetch your own community data
2. **External Profile** - Fetch data for another player by user-id
3. **Multiple Profiles** - Batch fetch data for multiple players

## Installation

```bash
# Install dependencies
uv sync

# Install Playwright browser
.venv/bin/playwright install chromium
```

## Usage

### Run the Scraper

```bash
python mytischtennis_scraper.py
```

You'll be prompted for:
1. **Username and password** - Your mytischtennis.de credentials
2. **Mode** - What you want to fetch
3. **Headed mode** - Whether to show the browser window (useful for debugging)

### Mode 1: Own Profile

Fetches your own community data and extracts tables:

```
Username (email): your@email.com
Password: ********

Select mode:
  1. Own profile
  2. External profile (by user-id)
  3. Multiple profiles

Mode [1-3]: 1
```

**Output files:**
- `tables/club_info.csv`
- `tables/ttr_rankings.csv`
- `tables/league_table.csv`
- `tables/ttr_history_events.csv`
- `tables/ttr_history_matches.csv`

### Mode 2: External Profile

Fetch data for another player using their user-id:

```
Mode [1-3]: 2
Enter user-id: 2fa35076-e634-457c-bf70-e89a70e0b7b0
Enter file prefix (optional, press Enter to use user-id):
```

**Output files:**
- `tables/2fa35076-e634-457c-bf70-e89a70e0b7b0_club_info.csv`
- `tables/2fa35076-e634-457c-bf70-e89a70e0b7b0_ttr_rankings.csv`
- `tables/2fa35076-e634-457c-bf70-e89a70e0b7b0_league_table.csv`
- `tables/2fa35076-e634-457c-bf70-e89a70e0b7b0_ttr_history_events.csv`
- `tables/2fa35076-e634-457c-bf70-e89a70e0b7b0_ttr_history_matches.csv`

**Finding user-ids:**
- User-ids can be found in URLs when viewing other players' profiles
- They look like: `2fa35076-e634-457c-bf70-e89a70e0b7b0`
- Example URL: `https://www.mytischtennis.de/community/external-profile?user-id=2fa35076-e634-457c-bf70-e89a70e0b7b0`

### Mode 3: Multiple Profiles

Fetch data for multiple players at once:

```
Mode [1-3]: 3
Enter user-ids (comma-separated): user-id-1,user-id-2,user-id-3
```

**Output files:**
- Tables prefixed with each user-id (e.g., `user-id-1_ttr_rankings.csv`)
- Enables comparison of multiple players' data

## Table Schema

### club_info.csv
| Column | Description |
|--------|-------------|
| clubNr | Club number |
| association | Federation (e.g., "ByTTV") |
| season | Current season |
| group_name | Full league name |
| group_name_short | Short league name |
| group_id | League group ID |
| extracted_at | Timestamp when data was extracted |

### ttr_rankings.csv
| Column | Description |
|--------|-------------|
| position | Position within club |
| firstname, lastname | Player name |
| rank | TTR rating |
| germanRank | German national rank |
| clubSexRank | Club position by gender |
| germanSexRank | German national rank by gender |
| fedRank | Federation rank |
| matchCount | Total matches played |
| clubName | Club name |
| personId | Person ID |

### league_table.csv
| Column | Description |
|--------|-------------|
| season | Current season |
| league | League name |
| group_id | League group ID |
| table_rank | Position in league table |
| teamname | Team name |
| own_points, other_points | Points scored/conceded |
| tendency | Recent performance trend (rise/steady/fall) |

### ttr_history_events.csv
| Column | Description |
|--------|-------------|
| event_date_time | Event date and time |
| formattedEventDate | Formatted date (DD.MM.YYYY) |
| event_name | Event name |
| event_id | Unique event ID |
| type | Event type (meeting/competition) |
| ttr_before, ttr_after | TTR rating before/after event |
| ttr_delta | TTR change |
| match_count, matches_won, matches_lost | Match statistics |

### ttr_history_matches.csv
| Column | Description |
|--------|-------------|
| event_id, event_name | Parent event information |
| match_number | Match number within event |
| own_person_name, other_person_name | Player names |
| other_ttr | Opponent's TTR |
| own_set1-7, other_set1-7 | Set scores |
| own_sets, other_sets | Total sets won |
| own_points, other_points | Match points (team events) |

## Advanced Usage

### Using as a Module

```python
from mytischtennis_scraper import MyTischtennisScraper

# Create scraper instance
scraper = MyTischtennisScraper(
    username="your@email.com",
    password="your-password",
    headless=True
)

# Login once
scraper.login()

# Fetch multiple profiles
user_ids = [
    "2fa35076-e634-457c-bf70-e89a70e0b7b0",
    "another-user-id-here"
]

results = scraper.run_multiple_profiles(user_ids)

# Or fetch individual profiles
for user_id in user_ids:
    scraper.run_external_profile(user_id, prefix=f"player_{user_id[:8]}_")
```

### Comparing Multiple Players

After fetching multiple profiles, you can compare them:

```python
import pandas as pd

# Load all TTR rankings
player1 = pd.read_csv('tables/user-id-1_ttr_rankings.csv')
player2 = pd.read_csv('tables/user-id-2_ttr_rankings.csv')

# Compare TTR changes
history1 = pd.read_csv('tables/user-id-1_ttr_history_events.csv')
history2 = pd.read_csv('tables/user-id-2_ttr_history_events.csv')
```

## Troubleshooting

### Login Issues
- Run in **headed mode** to see what's happening
- Check if the login form has changed
- Verify your credentials are correct

### Captcha Issues
- Use headed mode to manually solve captcha if needed
- The script automatically clicks checkbox captchas
- For complex captchas, you may need to intervene in headed mode

### Rate Limiting
- When fetching multiple profiles, the script adds 1-second delays between requests
- If you encounter rate limits, increase the delay in `run_multiple_profiles()`

## Data Privacy

- Your password is only used for login and never stored
- Cookies are extracted from the browser session for subsequent requests
- No credentials are saved to disk
- All fetched data belongs to you and the players you query

## API Endpoints

- **Own Profile**: `/community?show=everything&_data=routes%2F%24`
- **External Profile**: `/community/external-profile?user-id={ID}&show=everything&_data=routes%2F%24`

Both endpoints return the same JSON structure with:
- `pageContent.blockLoaderData` - Contains TTR rankings, league table
- Deferred data in response body - Contains TTR history with match details
