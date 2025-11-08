"""Tests for transient_scraper module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.transient_scraper import (
    TransientScraper,
    get_recent_transients,
    scrape_rochester_sn_page,
)


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code


@pytest.fixture
def sample_html() -> str:
    """Sample Rochester page HTML for testing."""
    return """
    <html>
    <body>
        <table>
            <tr><th>Name</th><th>Mag</th><th>Type</th></tr>
            <tr><td>AT2025abao</td><td>15.1</td><td>LRN</td></tr>
            <tr><td>AT2025abne</td><td>16.0</td><td>unknown</td></tr>
            <tr><td>SN2025abc</td><td>18.5</td><td>Ia</td></tr>
        </table>
        <p>AT2025test discovered 2025/01/15</p>
        <p>Mag 15.5 Type unknown</p>
    </body>
    </html>
    """


@pytest.fixture
def empty_html() -> str:
    """Empty HTML page for testing."""
    return "<html><body><p>No data</p></body></html>"


class TestTransientScraper:
    """Test suite for TransientScraper class."""

    def test_init(self) -> None:
        """Test TransientScraper initialization."""
        scraper = TransientScraper()
        assert scraper.sources is not None
        assert "rochester" in scraper.sources
        assert "rochesterastronomy" in scraper.sources["rochester"]

    @patch("src.transient_scraper.requests.get")
    def test_scrape_rochester_page(self, mock_get: Mock, sample_html: str) -> None:
        """Test scraping Rochester page with valid data."""
        mock_get.return_value = MockResponse(sample_html)
        scraper = TransientScraper()
        df = scraper.scrape_rochester_page()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "id" in df.columns
        assert "mag" in df.columns
        assert "type" in df.columns

    @patch("src.transient_scraper.requests.get")
    def test_get_recent_transients(self, mock_get: Mock, sample_html: str) -> None:
        """Test getting recent transients."""
        mock_get.return_value = MockResponse(sample_html)
        scraper = TransientScraper()
        df = scraper.get_recent_transients(days=7)

        assert isinstance(df, pd.DataFrame)


class TestScrapeFunctions:
    """Test suite for scraping functions."""

    @patch("src.transient_scraper.requests.get")
    def test_scrape_rochester_sn_page_success(self, mock_get: Mock, sample_html: str) -> None:
        """Test successful scraping of Rochester SN page."""
        mock_get.return_value = MockResponse(sample_html)
        df = scrape_rochester_sn_page()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert {"id", "mag", "type", "source"}.issubset(df.columns)
        assert len(df) >= 3

    @patch("src.transient_scraper.requests.get")
    def test_scrape_rochester_sn_page_empty(self, mock_get: Mock, empty_html: str) -> None:
        """Test scraping with empty page."""
        mock_get.return_value = MockResponse(empty_html)
        df = scrape_rochester_sn_page()

        assert isinstance(df, pd.DataFrame)

    @patch("src.transient_scraper.requests.get")
    def test_scrape_rochester_sn_page_network_error(self, mock_get: Mock) -> None:
        """Test scraping with network error."""
        mock_get.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            scrape_rochester_sn_page()

    @patch("src.transient_scraper.requests.get")
    def test_scrape_rochester_sn_page_deduplication(
        self, mock_get: Mock, sample_html: str
    ) -> None:
        """Test that duplicate entries are removed."""
        mock_get.return_value = MockResponse(sample_html)
        df = scrape_rochester_sn_page()

        # Check for duplicates
        assert df["id"].nunique() == len(df), "Found duplicate entries"

    @patch("src.transient_scraper.requests.get")
    def test_get_recent_transients_with_dates(self, mock_get: Mock) -> None:
        """Test filtering recent transients by date."""
        html_with_recent_date = """
        <html><body>
        <p>AT2025recent discovered 2025/11/01</p>
        <p>Mag 15.5 Type unknown</p>
        </body></html>
        """
        mock_get.return_value = MockResponse(html_with_recent_date)
        df = get_recent_transients(days=30)

        assert isinstance(df, pd.DataFrame)

    @patch("src.transient_scraper.requests.get")
    def test_magnitude_parsing(self, mock_get: Mock) -> None:
        """Test magnitude parsing from different formats."""
        html_with_mags = """
        <html><body>
        <table>
            <tr><th>Name</th><th>Mag</th><th>Type</th></tr>
            <tr><td>AT2025test1</td><td>15.1</td><td>unknown</td></tr>
            <tr><td>AT2025test2</td><td>16.5V</td><td>Ia</td></tr>
            <tr><td>AT2025test3</td><td>-</td><td>II</td></tr>
        </table>
        </body></html>
        """
        mock_get.return_value = MockResponse(html_with_mags)
        df = scrape_rochester_sn_page()

        assert df.loc[df["id"] == "AT2025test1", "mag"].values[0] == 15.1
        assert df.loc[df["id"] == "AT2025test2", "mag"].values[0] == 16.5
        assert pd.isna(df.loc[df["id"] == "AT2025test3", "mag"].values[0])

    @patch("src.transient_scraper.requests.get")
    def test_transient_name_filtering(self, mock_get: Mock) -> None:
        """Test that only AT and SN prefixed names are kept."""
        html_with_names = """
        <html><body>
        <table>
            <tr><th>Name</th><th>Mag</th><th>Type</th></tr>
            <tr><td>AT2025test</td><td>15.0</td><td>unknown</td></tr>
            <tr><td>SN2025test</td><td>16.0</td><td>Ia</td></tr>
            <tr><td>InvalidName</td><td>17.0</td><td>II</td></tr>
        </table>
        </body></html>
        """
        mock_get.return_value = MockResponse(html_with_names)
        df = scrape_rochester_sn_page()

        assert all(df["id"].str.startswith(("AT", "SN")))
        assert "InvalidName" not in df["id"].values


@pytest.mark.integration
class TestIntegrationScraping:
    """Integration tests that may require network access."""

    @pytest.mark.skip(reason="Requires network access - run manually")
    def test_live_scraping(self) -> None:
        """Test live scraping of Rochester page."""
        df = scrape_rochester_sn_page()
        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert "id" in df.columns
            assert all(df["id"].str.startswith(("AT", "SN")))
