"""Tests for MyTischtennisScraper"""

import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from mytt_scraper import MyTischtennisScraper


def test_parse_multipart_json():
    """Test multipart JSON parsing"""
    from mytt_scraper.utils import parse_multipart_json

    # Simple test case
    json_text = '{"test": "value"}some extra text'

    data, remaining = parse_multipart_json(json_text)

    assert data == {"test": "value"}
    assert remaining == "some extra text"
    print("✓ test_parse_multipart_json passed")


def test_scraper_initialization():
    """Test scraper initialization"""
    scraper = MyTischtennisScraper("test@example.com", "password", headless=True)

    assert scraper.username == "test@example.com"
    assert scraper.password == "password"
    assert scraper.headless is True
    assert scraper.tables_dir.exists()
    print("✓ test_scraper_initialization passed")


if __name__ == "__main__":
    test_parse_multipart_json()
    test_scraper_initialization()
    print("\nAll tests passed!")
