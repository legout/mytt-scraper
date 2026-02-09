#!/bin/bash
# Setup script for mytt-scraper

echo "=== Setting up mytt-scraper ==="
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

echo ""
echo "=== Setup complete! ==="
echo "You can now run the scraper with: python mytischtennis_scraper.py"
