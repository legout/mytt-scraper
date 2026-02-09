# mytt-scraper

A Python package to login to mytischtennis.de and fetch player data including TTR rankings, league tables, and match history.

## Features

- ✅ **Automatic login** with Playwright browser automation
- ✅ **Captcha handling** - automatically clicks checkbox captchas
- ✅ **Multiple modes**:
  - Own profile data
  - External profile (by user-id)
  - Batch fetch for multiple players
  - Player search
  - Search and fetch
- ✅ **Automatic table extraction** - saves data as flat CSV files
- ✅ **Complete history** - TTR changes, match scores, opponents
- ✅ **Player search** - Find opponents by name or club

## Quick Start

### Installation

```bash
# Install dependencies
uv sync

# Install Playwright browser
.venv/bin/playwright install chromium
```

### Run the Scraper

```bash
# Run CLI script
python -m mytt_scraper.cli

# Or run TUI
python -m mytt_scraper.tui
```

## Documentation

- **[Tutorials](tutorials/)** - Learning-oriented guides for beginners
- **[How-To Guides](how-to/)** - Task-oriented directions for specific goals
- **[Reference](reference/)** - Technical information about API and data structures
- **[Explanation](explanation/)** - Background information and conceptual guides

## Output Files

All extracted data is saved as CSV files in the `tables/` directory:

| File | Description |
|-------|-------------|
| `club_info.csv` | Club and league information |
| `ttr_rankings.csv` | TTR rankings within club |
| `league_table.csv` | League standings |
| `ttr_history_events.csv` | TTR change history (events) |
| `ttr_history_matches.csv` | Detailed match scores |

## License

MIT License - see [LICENSE](https://github.com/legout/mytt-scraper/blob/main/LICENSE) for details.
