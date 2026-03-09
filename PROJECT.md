# PROJECT: mytt-scraper

## Mission

A Python scraper tool with TUI and WebUI for extracting personal table tennis data from mytischtennis.de. Enables players to fetch their TTR rankings, league tables, match history, and perform player searches through both an interactive terminal interface and programmatic API.

## Users / Stakeholders

- **Primary Users:** Table tennis players in Germany who want to analyze their own performance data
- **Secondary Users:** Coaches and team captains scouting opponent players
- **Developers:** Those extending the scraper or integrating it into other tools

## Goals

1. Provide reliable automated login to mytischtennis.de with captcha handling
2. Extract structured data (TTR rankings, league tables, match history) as CSV or in-memory DataFrames
3. Offer an intuitive TUI (Textual) for interactive data exploration
4. Support batch operations for multiple player profiles
5. Enable player search by name/club with multi-select fetch
6. Provide in-memory table extraction with Polars/Pandas/PyArrow backends
7. Include interactive table viewer with filtering, sorting, and SQL queries

## Non-Goals

- **Not** a general-purpose web scraper framework
- **Not** designed for high-frequency automated data harvesting (respects rate limits)
- **Not** a data analysis or visualization tool (outputs data for external analysis)
- **Not** affiliated with or endorsed by mytischtennis.de
- **Not** for commercial data resale

## Domain Model / Glossary

| Term | Definition |
|------|------------|
| **TTR** | Tischtennis Rating - German table tennis ranking system |
| **MyTischtennis** | The website mytischtennis.de - largest German table tennis community platform |
| **Community Data** | Player profile information including clubs, leagues, rankings |
| **League Table** | Standings for a player's league/division |
| **TTR History** | Time-series of TTR changes with match details |
| **Headed Mode** | Browser automation with visible window (for debugging) |
| **Headless Mode** | Browser automation without visible window (default) |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Entry Points                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │ CLI      │  │ TUI      │  │ Library (Python API)     │  │
│  │ scripts/ │  │ textual  │  │ mytt_scraper package     │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────────┘  │
└───────┼─────────────┼───────────────────┼──────────────────┘
        │             │                   │
        └─────────────┴───────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Scraper    │  │Player Search │  │Table Extractor│
│  (scraper.py)│  │(player_search│  │(table_*.py)   │
│              │  │    .py)      │  │               │
└──────┬───────┘  └──────┬───────┘  └───────┬───────┘
       │                 │                  │
       └─────────────────┴──────────────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
            ┌──────────┐  ┌──────────┐
            │Playwright│  │  API     │
            │  (auth)  │  │(requests)│
            └────┬─────┘  └────┬─────┘
                 │             │
                 └──────┬──────┘
                        ▼
               ┌────────────────┐
               │mytischtennis.de│
               └────────────────┘
```

### Key Components

1. **MyTischtennisScraper** (`scraper.py`): Core class handling login and data fetching
2. **PlayerSearcher** (`player_search.py`): Extends scraper with search capabilities
3. **TUI** (`tui/`): Textual-based interactive interface with screens for login, menu, search, batch fetch, and table viewing
4. **Table Extraction** (`utils/table_*.py`): Converts raw JSON to structured DataFrames/CSV
5. **Query Engine** (`utils/query_*.py`): DuckDB-based SQL querying and filtering for TUI table viewer

## Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.13+ |
| **Package Manager** | uv |
| **Browser Automation** | Playwright |
| **HTTP Requests** | requests |
| **Data Processing** | Polars (default), Pandas, PyArrow |
| **Query Engine** | DuckDB |
| **TUI Framework** | Textual |
| **Testing** | pytest |
| **Linting/Formatting** | ruff |
| **Type Checking** | mypy |
| **Documentation** | Zensical (Diátaxis structure) |
| **CI/CD** | GitHub Actions |

## Constraints

1. **External Dependency:** Relies on mytischtennis.de website structure (fragile to UI changes)
2. **Authentication Required:** Valid credentials needed; captcha handling may require manual intervention
3. **Rate Limiting:** Built-in delays between requests to avoid being blocked
4. **Legal/Ethical:** For personal use only; must respect ToS
5. **Browser Requirement:** Playwright with Chromium for initial login

## Quality Bar

- All code formatted with `ruff format`
- All code passes `ruff check` linting
- Type hints required; checked with `mypy`
- Tests for core functionality in `tests/`
- Documentation in Diátaxis structure (tutorials, how-to, reference, explanation)

## Invariants

1. **Never store credentials:** Session-only authentication; no password persistence
2. **CSV output:** Flat table extraction always produces consistent column schemas
3. **Backend agnostic:** Table extraction supports Polars, Pandas, and PyArrow
4. **Graceful degradation:** Missing data results in omitted tables, not crashes

## Current Reality

- **Mature TUI:** Fully functional Textual interface with login, search, batch fetch, and interactive table viewer
- **Query System:** DuckDB-based SQL queries, filtering, sorting, and aggregation in table viewer
- **Library API:** Clean programmatic interface for embedding in other tools
- **Documentation:** Diátaxis-structured docs with Zensical site generator
- **Test Coverage:** Core table and query functionality tested
- **Active Development:** Many tickets resolved; .tf/ knowledge base established
- **Technical Debt:** Some scraper code tied to specific DOM selectors; may break on site updates

## Baseline Guides

- [Coding Standards](.tf/knowledge/baselines/coding-standards.md)
- [Testing](.tf/knowledge/baselines/testing.md)
- [Architecture](.tf/knowledge/baselines/architecture.md)

## Source-of-Truth References

- [README.md](README.md) - User-facing documentation
- [pyproject.toml](pyproject.toml) - Dependencies and project config
- [docs/](docs/) - Full documentation site source
