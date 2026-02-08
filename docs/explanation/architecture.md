# System Architecture

This page explains how mytt-scraper works under the hood — the journey of a data request from your command line to structured tables on your disk.

## Overview

mytt-scraper follows a **hybrid automation pattern**: it uses browser automation only where necessary (authentication), then switches to efficient HTTP requests for data retrieval. This architecture balances reliability with performance.

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   You       │────▶│  Playwright  │────▶│   Cookies   │────▶│   requests   │
│  (CLI/API)  │     │   (Login)    │     │  (Session)  │     │  (Fetch API) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────┬───────┘
                                                                     │
                                                                     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Tables    │◀────│    CSV or    │◀────│  Extract &  │◀────│  Response    │
│  (Output)   │     │  DataFrames  │     │   Flatten   │     │  (JSON/MPJ)  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

## The Data Flow

### Step 1: Browser Authentication (Playwright)

The mytischtennis.de website uses a combination of traditional form-based authentication and modern anti-bot protections. We use Playwright because:

- **JavaScript-rendered login forms** — The login page requires JavaScript to function
- **Captcha handling** — The site presents checkbox captchas that need visual interaction
- **Cookie-based sessions** — The authentication tokens are stored as HTTP cookies

When you call `login()`:

```python
from mytt_scraper import MyTischtennisScraper

scraper = MyTischtennisScraper("user@example.com", "password")
scraper.login()  # Browser automation happens here
```

Behind the scenes:

1. Playwright launches a Chromium browser (headless by default)
2. Navigates to the login page
3. Fills in your credentials
4. Handles any captcha checkbox automatically
5. Submits the form and waits for navigation
6. Extracts all cookies from the authenticated session
7. Closes the browser

The result is a set of session cookies that authenticate subsequent requests.

### Step 2: Session Transfer (Cookies)

After browser authentication, the cookies are transferred to a `requests.Session`:

```python
# Inside login flow
cookies = await context.cookies()  # From Playwright
for cookie in cookies:
    self.session.cookies[cookie['name']] = cookie['value']
```

This transfer is crucial because it lets us:

- **Reuse the authenticated session** — No need to open another browser
- **Make fast HTTP requests** — requests is much faster than browser automation
- **Maintain session state** — Cookies are valid for the session duration

### Step 3: Data Retrieval (HTTP Requests)

With authenticated cookies in place, data fetching uses standard HTTP GET requests:

```python
# After login, this is just an HTTP request
response = self.session.get(
    "https://www.mytischtennis.de/community?show=everything&_data=routes%2F%24"
)
```

The mytischtennis.de site returns data as **multipart JSON** (a Remix framework pattern):

```
--boundary
Content-Type: application/json

{"pageContent": {...}}
--boundary
Content-Type: application/json

{"deferredData": {...}}
--boundary--
```

Our parser splits this into:

- **`data`** — The main response with club info, rankings, league tables
- **`remaining`** — Deferred TTR history data (loaded asynchronously by the site)

### Step 4: Table Extraction (Normalization)

The raw JSON is deeply nested. We flatten it into relational tables:

```python
data, remaining = scraper.fetch_own_community()
tables = scraper.extract_flat_tables(data, remaining, backend="polars")

# tables is now a dict of DataFrames:
# - club_info: Single-row table with club details
# - ttr_rankings: List of club members and their ratings
# - league_table: Current league standings
# - ttr_history_events: Summary of TTR-changing events
# - ttr_history_matches: Individual matches from events
```

See [Table Relationships](table-relationships.md) for how these tables connect.

## Why This Architecture?

### Why Not Just Requests?

Modern websites increasingly rely on:

- **JavaScript for authentication** — CSRF tokens generated client-side
- **Bot detection** — Headless detection, fingerprinting, behavior analysis
- **Captcha services** — Google reCAPTCHA, Cloudflare challenges

By using Playwright for login, we bypass these protections legitimately — you're a real user logging in, just automated.

### Why Not Full Browser Automation?

Once authenticated, continuing with browser automation would be:

- **Slower** — Page loads, renders, executes JavaScript
- **Heavier** — Memory-intensive browser processes
- **More fragile** — DOM selectors break when UI changes

HTTP requests are 10-50x faster and more reliable for API-like data fetching.

### Why Multipart JSON?

The mytischtennis.de site uses the Remix web framework, which:

1. Streams initial page data immediately
2. Defers expensive queries (like TTR history) separately
3. Combines both into a single HTTP response using multipart encoding

Our `parse_multipart_json()` function handles this transparently.

## Component Breakdown

| Component | Responsibility | Key File |
|-----------|---------------|----------|
| **Auth** (`utils/auth.py`) | Browser login, captcha handling, cookie extraction | `auth.py` |
| **Scraper** (`scraper.py`) | High-level workflow, session management | `scraper.py` |
| **Extractor** (`utils/table_extractor.py`) | CSV file writing, normalization | `table_extractor.py` |
| **In-Memory** (`utils/in_memory_tables.py`) | DataFrame creation, backend abstraction | `in_memory_tables.py` |
| **Search** (`player_search.py`) | Player discovery via API or browser | `player_search.py` |

## Security Considerations

### Credential Handling

- **Never stored** — Credentials are only used during login
- **Memory-only** — Password exists only in RAM during the login call
- **No logging** — Credentials are not written to logs or output

### Session Security

- **Session cookies only** — We extract session tokens, not your password
- **Same-origin requests** — All authenticated requests go to mytischtennis.de
- **No third parties** — Your data is not sent anywhere else

### Rate Limiting

The scraper includes built-in rate limiting:

- **1-second delays** between profile fetches in batch mode
- **Respectful defaults** — Designed for personal use, not bulk scraping

See [Rate Limiting and Ethics](rate-limiting-ethics.md) for responsible usage guidelines.

## Data Consistency

The architecture ensures you get complete, consistent data:

1. **Atomic fetch** — All tables come from the same request (same timestamp)
2. **Referential integrity** — `event_id` in matches table exists in events table
3. **No partial writes** — Extraction happens in memory; files are written atomically

## Error Handling

Each step has specific error handling:

| Step | Failure Mode | Recovery |
|------|--------------|----------|
| Login | Wrong credentials, captcha fail | Return `False`, user retries |
| Cookie transfer | No auth cookies | Detected, login marked failed |
| Fetch | Network error, 401/403 | Return `None`, propagate error |
| Parse | Invalid JSON | Exception with partial data |
| Extraction | Missing fields | Graceful skip, log warning |

## See Also

- **[Python API Reference](../reference/python-api.md)** — Complete API documentation
- **[CLI Reference](../reference/cli.md)** — Command-line interface details
- **[Authentication Flow](authentication-flow.md)** — Deep dive into login mechanics
- **[Why Playwright?](why-playwright.md)** — Browser automation rationale
- **[Rate Limiting and Ethics](rate-limiting-ethics.md)** — Responsible usage
- **[In-Memory vs Disk Tables](in-memory-vs-disk-tables.md)** — Data workflow choices
