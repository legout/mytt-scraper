# TTR Data Tables

This directory contains flat CSV tables extracted from `ttr_data.json`.

## Tables Overview

### 1. club_info.csv
General information about the club and league.

**Columns:**
- `name` - Club name (may be null)
- `clubNr` - Club number
- `association` - Federation (e.g., "ByTTV")
- `season` - Current season (e.g., "25/26")
- `group_name` - Full league name
- `group_name_short` - Short league name
- `group_id` - League group ID
- `extracted_at` - Timestamp when data was extracted

**Rows:** 1

---

### 2. ttr_rankings.csv
Player rankings within the club.

**Columns:**
- `position` - Position within club
- `firstname` - Player first name
- `lastname` - Player last name
- `rank` - TTR rating
- `germanRank` - German national rank
- `clubSexRank` - Club position by gender
- `germanSexRank` - German national rank by gender
- `fedRank` - Federation rank
- `clubName` - Club name
- `clubNr` - Club number
- `personId` - Person ID
- `matchCount` - Total matches played
- `fewGames` - Games count
- `gender` - Player gender
- `country` - Player country
- `continent` - Player continent
- `fedNickname` - Federation nickname
- `external_id` - External ID
- `lastYearNoGames` - Whether player had no games last year

**Rows:** 5 (players in the club)

---

### 3. league_table.csv
Current league standings.

**Columns:**
- `season` - Current season
- `league` - League name
- `group_id` - League group ID
- `table_rank` - Position in league table
- `teamname` - Team name
- `club_nr` - Club number
- `team_id` - Team ID
- `own_points` - Points scored
- `other_points` - Points conceded
- `tendency` - Recent performance trend (rise/steady/fall)

**Rows:** 5 (teams in the league)

---

### 4. ttr_history_events.csv
Summary of all TTR events (team meetings, tournaments, etc.).

**Columns:**
- `event_date_time` - Event date and time
- `formattedEventDate` - Formatted date (DD.MM.YYYY)
- `formattedEventTime` - Formatted time (HH:MM)
- `event_name` - Event name (e.g., "BL-Erwachsene | TSV Grombühl Würzburg II : TSV Güntersleben")
- `event_id` - Unique event ID
- `type` - Event type (meeting/competition)
- `ttr_before` - TTR rating before event
- `ttr_after` - TTR rating after event
- `ttr_delta` - TTR change
- `match_count` - Number of matches in event
- `matches_won` - Matches won
- `matches_lost` - Matches lost
- `expected_result` - Expected result score
- `alteration_constant` - TTR alteration constant

**Rows:** 519 (historical events)

---

### 5. ttr_history_matches.csv
Individual match details within each event.

**Columns:**
- `event_id` - Parent event ID
- `event_name` - Parent event name
- `event_date_time` - Event date and time
- `formattedEventDate` - Formatted date
- `formattedEventTime` - Formatted time
- `event_type` - Event type (meeting/tournament)
- `match_number` - Match number within event
- `type` - Match type (meeting/tournament)
- `own_person_id` - Your person ID
- `own_person_name` - Your name
- `own_team_name` - Your team name
- `own_ttr` - Your TTR (may be empty)
- `other_person_id` - Opponent person ID
- `other_person_name` - Opponent name
- `other_team_name` - Opponent team name
- `other_ttr` - Opponent TTR
- `ttr_before` - TTR before event
- `ttr_after` - TTR after event
- `scheduled` - Scheduled date/time
- `expected_result` - Expected win probability
- `own_set1` through `own_set7` - Your set scores
- `other_set1` through `other_set7` - Opponent set scores
- `own_sets` - Total sets you won
- `other_sets` - Total sets opponent won
- `own_points` - Match points (team event points)
- `other_points` - Opponent match points
- `other_w_r_l` - Other win/loss/record

**Rows:** 23 (only events with detailed match data)

**Note:** Not all events in the TTR history have detailed match data. Some older events are summarized with only the event-level information.

---

## Relationships

```
club_info (1)
    │
    ├── league_table (many teams)
    │
    ├── ttr_rankings (many players)
    │
    └── ttr_history_events (many events)
            │
            └── ttr_history_matches (many matches per event)
```

## Data Integrity

- **ttr_rankings**: All player ranking data for the club
- **league_table**: All teams in the current league
- **ttr_history_events**: Complete history of TTR changes (519 events)
- **ttr_history_matches**: Detailed match breakdown (only for recent events with full data)

## Usage Examples

### Load into Python

```python
import pandas as pd

# Load all tables
rankings = pd.read_csv('ttr_rankings.csv')
league = pd.read_csv('league_table.csv')
events = pd.read_csv('ttr_history_events.csv')
matches = pd.read_csv('ttr_history_matches.csv')

# Example: Find your TTR trend
events['event_date'] = pd.to_datetime(events['event_date_time'])
recent = events.sort_values('event_date', ascending=False).head(10)
print(recent[['formattedEventDate', 'event_name', 'ttr_before', 'ttr_after', 'ttr_delta']])
```

### Load into SQL

```sql
CREATE TABLE ttr_rankings (
    position INTEGER,
    firstname TEXT,
    lastname TEXT,
    rank INTEGER,
    germanRank INTEGER,
    -- ... other columns
);

-- Import: sqlite3 mytt.db < import.sql
-- Or use COPY command in PostgreSQL
```

### Load into Excel

Simply open any `.csv` file in Excel, or import via Data > Get Data > From Text/CSV.
