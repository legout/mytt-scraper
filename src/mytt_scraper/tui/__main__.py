"""Entry point for `python -m mytt_scraper.tui`."""

import sys

from .app import MyttScraperApp


def main() -> int:
    """Run the TUI application.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        app = MyttScraperApp()
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())