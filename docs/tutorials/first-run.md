# Tutorial: First Run

Welcome! This tutorial will take you from a fresh installation to successfully fetching your first mytischtennis.de profile data. By the end, you'll have extracted your TTR rankings, league tables, and match history as CSV files.

## What You'll Learn

- Install the project dependencies
- Set up Playwright for browser automation
- Log in to mytischtennis.de
- Fetch your own profile data
- Find your extracted data files

## Prerequisites

- Python 3.10 or higher
- A mytischtennis.de account (with valid credentials)
- Internet connection

---

## Step 1: Install Dependencies

First, ensure you have `uv` installed (a fast Python package manager):

```bash
# Check if uv is installed
uv --version

# If not installed, install it:
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Now install the project dependencies:

```bash
# Clone or navigate to the project directory
cd mytt-scraper

# Install dependencies using uv
uv sync
```

You'll see output showing package downloads and installation progress. This creates a virtual environment in `.venv/` with all required packages.

---

## Step 2: Install Playwright Browser

Playwright is the browser automation tool that handles login and captchas. You need to install the browser binaries:

```bash
# Install Chromium browser for Playwright
.venv/bin/playwright install chromium
```

This downloads approximately 100-150MB of browser files. It may take a few minutes depending on your connection.

**Expected output:**
```
Downloading Chromium...
Chromium downloaded to ...
```

---

## Step 3: Run the Scraper

Now you're ready to fetch your data. Run the main script:

```bash
# Run the CLI script
python scripts/main.py
```

---

## Step 4: Enter Your Credentials

The script will prompt you for your mytischtennis.de credentials:

```
=== MyTischtennis.de Scraper ===

Username (email): your.email@example.com
Password: 
```

**Important security notes:**
- Your password is hidden when typing (standard security practice)
- Credentials are used only for login and are never stored to disk
- The script creates a browser session but doesn't save your password

---

## Step 5: Select Mode 1 (Own Profile)

After entering credentials, you'll see the mode selection menu:

```
Select mode:
  1. Own profile
  2. External profile (by user-id)
  3. Multiple profiles
  4. Search for players
  5. Search and fetch

Mode [1-5]: 1
```

Type `1` and press Enter to fetch your own profile data.

---

## Step 6: Choose Headless or Headed Mode

Next, you'll be asked about the browser mode:

```
Run in headed mode? (shows browser window) [y/N]: 
```

**For your first run, we recommend headed mode:**
- Type `y` and press Enter
- This opens a visible browser window so you can see what's happening
- Useful for troubleshooting if any issues occur

For subsequent runs, you can use headless mode (just press Enter for the default `N`) for faster, background operation.

---

## Step 7: Wait for Login and Data Fetch

The script will now:
1. Open a browser window (in headed mode)
2. Navigate to mytischtennis.de
3. Log in with your credentials
4. Handle any captcha automatically
5. Navigate to your community profile
6. Extract all available data

**Expected output:**
```
✓ Own profile data extracted!
```

The browser window will close automatically when complete.

---

## Step 8: Find Your Extracted Data

All extracted data is saved as CSV files in the `tables/` directory:

```bash
# List the extracted files
ls -la tables/
```

**You should see files like:**

| File | Contents |
|------|----------|
| `club_info.csv` | Your club and league information |
| `ttr_rankings.csv` | TTR rankings within your club |
| `league_table.csv` | Your league standings |
| `ttr_history_events.csv` | TTR change history (events) |
| `ttr_history_matches.csv` | Detailed match scores |

**Example - View your TTR ranking:**

```bash
# View the TTR rankings (macOS/Linux)
cat tables/ttr_rankings.csv

# Or open in a spreadsheet application
open tables/ttr_rankings.csv  # macOS
xdg-open tables/ttr_rankings.csv  # Linux
```

---

## Troubleshooting

### "playwright install chromium" fails

**Problem:** Browser installation fails or hangs.

**Solution:**
```bash
# Try with explicit path
python -m playwright install chromium

# Or reinstall uv environment
rm -rf .venv
uv sync
.venv/bin/playwright install chromium
```

### Login fails in headless mode

**Problem:** Script fails to log in when running headless.

**Solution:**
- Run in **headed mode** (`y` when asked) to see what's happening
- Check if your credentials work on the website directly
- Verify your internet connection
- Some accounts may require headed mode for the first login

### Captcha issues

**Problem:** Script gets stuck at captcha or fails to proceed.

**Solution:**
- Run in **headed mode** (`y` when asked)
- The script handles checkbox captchas automatically
- For complex captchas, the browser will pause for manual intervention
- Complete the captcha manually in the browser window
- The script will continue automatically after captcha is solved

### "No data extracted" or empty tables

**Problem:** Script runs but CSV files are empty or missing.

**Solution:**
- Ensure you're logged in to mytischtennis.de in a regular browser first
- Check that your profile is public and has data
- Verify your account has community access enabled
- Check the browser window (headed mode) for any error messages

### Permission denied errors

**Problem:** Cannot write to `tables/` directory.

**Solution:**
```bash
# Create the directory manually if it doesn't exist
mkdir -p tables

# Check permissions
chmod 755 tables
```

### Script hangs or times out

**Problem:** Script appears stuck during login or data fetch.

**Solution:**
- Press `Ctrl+C` to cancel
- Run in headed mode to see what's happening
- Check if mytischtennis.de is accessible in your browser
- Wait times can vary; give it up to 60 seconds for login

---

## Next Steps

Congratulations! You've successfully extracted your mytischtennis.de data. Here's what you can do next:

### Analyze Your Data

The CSV files can be opened in:
- **Excel** or **Google Sheets** for spreadsheet analysis
- **Python** with pandas/polars for programmatic analysis
- **Any text editor** to view raw data

### Try Other Modes

Now that you've completed your first run, explore other modes:

- **Mode 2** - Fetch another player's profile (requires their user-id)
- **Mode 4** - Search for players by name
- **Mode 5** - Search and fetch multiple players at once

See the [How-To Guides](../how-to/index.md) for detailed instructions on each mode.

### Use the TUI (Textual User Interface)

For a more interactive experience, try the TUI:

```bash
python -m mytt_scraper.tui
```

The TUI provides a visual interface with:
- Interactive player search with checkboxes
- Real-time progress bars
- Built-in table viewer with filtering and sorting

---

## Summary

You've completed the first-run tutorial! Here's what you did:

1. ✅ Installed dependencies with `uv sync`
2. ✅ Installed Playwright browser with `.venv/bin/playwright install chromium`
3. ✅ Ran the scraper with `python scripts/main.py`
4. ✅ Logged in with your mytischtennis.de credentials
5. ✅ Selected Mode 1 (Own Profile)
6. ✅ Successfully extracted data to `tables/` directory

Your data is now available as CSV files ready for analysis. Happy scraping!

---

## Need Help?

- **How-To Guides** - Solutions for specific tasks: [../how-to/index.md](../how-to/index.md)
- **Reference** - Technical details and API docs: [../reference/index.md](../reference/index.md)
- **Explanation** - Understanding how it works: [../explanation/index.md](../explanation/index.md)
