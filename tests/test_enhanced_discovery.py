"""Tests for enhanced_discovery_v2 module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.enhanced_discovery_v2 import EnhancedDiscoveryEngineV2


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code


@pytest.fixture
def engine() -> EnhancedDiscoveryEngineV2:
    """Create an EnhancedDiscoveryEngineV2 instance for testing."""
    return EnhancedDiscoveryEngineV2()


@pytest.fixture
def sample_transients() -> pd.DataFrame:
    """Sample transient data for testing."""
    return pd.DataFrame(
        [
            {"id": "AT2025abao", "mag": 15.1, "type": "LRN", "source": "Rochester"},
            {"id": "AT2025abne", "mag": 16.0, "type": "unknown", "source": "Rochester"},
            {"id": "SN2025abc", "mag": 18.5, "type": "Ia", "source": "Rochester"},
            {"id": "AT2025test", "mag": 13.5, "type": "unknown", "source": "Rochester"},
            {"id": "SN2025iip", "mag": 17.5, "type": "IIP", "source": "Rochester"},
            {"id": "SN2025ibn", "mag": 16.5, "type": "Ibn", "source": "Rochester"},
        ]
    )


class TestEnhancedDiscoveryEngineV2:
    """Test suite for EnhancedDiscoveryEngineV2 class."""

    def test_init(self, engine: EnhancedDiscoveryEngineV2) -> None:
        """Test engine initialization."""
        assert isinstance(engine.transients, pd.DataFrame)
        assert isinstance(engine.anomalies, list)
        assert engine.transients.empty
        assert len(engine.anomalies) == 0

    def test_calculate_advanced_score_bright_object(
        self, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test scoring for bright objects."""
        row = pd.Series({"id": "AT2025test", "mag": 13.5, "type": "unknown"})
        score, reasons = engine.calculate_advanced_score(row)

        assert score >= 5.0
        assert any("bright" in r.lower() for r in reasons)

    def test_calculate_advanced_score_rare_type(self, engine: EnhancedDiscoveryEngineV2) -> None:
        """Test scoring for rare types."""
        row = pd.Series({"id": "AT2025test", "mag": 15.1, "type": "LRN"})
        score, reasons = engine.calculate_advanced_score(row)

        assert score >= 5.0
        assert any("rare" in r.lower() for r in reasons)

    def test_calculate_advanced_score_unknown_type(
        self, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test scoring for unknown types."""
        row = pd.Series({"id": "AT2025test", "mag": 16.0, "type": "unknown"})
        score, reasons = engine.calculate_advanced_score(row)

        assert score > 0.0

    def test_calculate_advanced_score_faint_object(
        self, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test scoring for extremely faint objects."""
        row = pd.Series({"id": "AT2025test", "mag": 22.0, "type": "Ia"})
        score, reasons = engine.calculate_advanced_score(row)

        assert score > 0.0
        assert any("faint" in r.lower() for r in reasons)

    def test_calculate_advanced_score_ibn_type(self, engine: EnhancedDiscoveryEngineV2) -> None:
        """Test scoring for Ibn type supernovae."""
        row = pd.Series({"id": "SN2025test", "mag": 16.5, "type": "Ibn"})
        score, reasons = engine.calculate_advanced_score(row)

        assert score >= 4.0
        assert any("rare" in r.lower() for r in reasons)

    def test_find_advanced_anomalies(
        self, engine: EnhancedDiscoveryEngineV2, sample_transients: pd.DataFrame
    ) -> None:
        """Test finding anomalies with advanced scoring."""
        anomalies = engine.find_advanced_anomalies(sample_transients)

        assert isinstance(anomalies, list)
        assert len(anomalies) > 0
        assert all("score" in a for a in anomalies)
        assert all("id" in a for a in anomalies)
        assert all("reasons" in a for a in anomalies)

        # Check sorting
        scores = [a["score"] for a in anomalies]
        assert scores == sorted(scores, reverse=True)

    def test_find_advanced_anomalies_filters_low_scores(
        self, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test that low-scoring objects are filtered out."""
        low_score_data = pd.DataFrame(
            [
                {"id": "SN2025normal", "mag": 18.0, "type": "Ia", "source": "Rochester"},
                {"id": "SN2025normal2", "mag": 19.0, "type": "II", "source": "Rochester"},
            ]
        )

        anomalies = engine.find_advanced_anomalies(low_score_data)
        assert len(anomalies) == 0

    def test_find_advanced_anomalies_with_coordinates(
        self, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test anomaly finding with coordinate data."""
        data_with_coords = pd.DataFrame(
            [
                {
                    "id": "AT2025test",
                    "mag": 13.5,
                    "type": "unknown",
                    "source": "Rochester",
                    "ra": "12h30m45s",
                    "dec": "+45d30m15s",
                }
            ]
        )

        anomalies = engine.find_advanced_anomalies(data_with_coords)
        assert len(anomalies) > 0
        assert "ra" in anomalies[0]
        assert "dec" in anomalies[0]

    def test_generate_advanced_report_no_anomalies(
        self, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test report generation with no anomalies."""
        report = engine.generate_advanced_report([])

        assert isinstance(report, str)
        assert "No high-priority anomalies" in report
        assert "ASTRA ADVANCED DISCOVERY REPORT" in report

    def test_generate_advanced_report_with_anomalies(
        self, engine: EnhancedDiscoveryEngineV2, sample_transients: pd.DataFrame
    ) -> None:
        """Test report generation with anomalies."""
        anomalies = engine.find_advanced_anomalies(sample_transients)
        report = engine.generate_advanced_report(anomalies)

        assert isinstance(report, str)
        assert "ASTRA ADVANCED DISCOVERY REPORT" in report
        assert "HIGH-PRIORITY ANOMALIES" in report
        assert "IMMEDIATE FOLLOW-UP REQUIRED" in report
        assert "SCIENCE OPPORTUNITIES" in report

    def test_generate_advanced_report_priority_levels(
        self, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test report contains correct priority levels."""
        high_priority_anomalies = [
            {
                "id": "AT2025high",
                "mag": 13.0,
                "type": "LRN",
                "score": 8.0,
                "reasons": ["Exceptionally bright", "Rare type"],
                "source": "Rochester",
            },
            {
                "id": "AT2025medium",
                "mag": 15.5,
                "type": "unknown",
                "score": 5.5,
                "reasons": ["Very bright"],
                "source": "Rochester",
            },
        ]

        report = engine.generate_advanced_report(high_priority_anomalies)

        assert "🔴 HIGH" in report or "HIGH" in report
        assert "🟡 MEDIUM" in report or "MEDIUM" in report

    @patch("src.enhanced_discovery_v2.requests.get")
    def test_scrape_rochester_enhanced(self, mock_get: Mock, engine: EnhancedDiscoveryEngineV2) -> None:
        """Test enhanced Rochester scraping."""
        sample_html = """
        <html><body>
        <table>
            <tr><th>Name</th><th>Mag</th><th>Type</th></tr>
            <tr><td>AT2025test</td><td>15.1</td><td>unknown</td></tr>
        </table>
        </body></html>
        """
        mock_get.return_value = MockResponse(sample_html)

        df = engine.scrape_rochester_enhanced()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "id" in df.columns

    @patch("src.enhanced_discovery_v2.requests.get")
    def test_run_advanced_pipeline_success(
        self, mock_get: Mock, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test complete advanced pipeline execution."""
        sample_html = """
        <html><body>
        <table>
            <tr><th>Name</th><th>Mag</th><th>Type</th></tr>
            <tr><td>AT2025test</td><td>13.5</td><td>LRN</td></tr>
        </table>
        </body></html>
        """
        mock_get.return_value = MockResponse(sample_html)

        results = engine.run_advanced_pipeline()

        assert results is not None
        assert "transients" in results
        assert "anomalies" in results
        assert "report" in results
        assert isinstance(results["transients"], pd.DataFrame)
        assert isinstance(results["anomalies"], list)
        assert isinstance(results["report"], str)

    @patch("src.enhanced_discovery_v2.requests.get")
    def test_run_advanced_pipeline_no_data(
        self, mock_get: Mock, engine: EnhancedDiscoveryEngineV2
    ) -> None:
        """Test pipeline with no data found."""
        mock_get.return_value = MockResponse("<html><body></body></html>")

        results = engine.run_advanced_pipeline()

        assert results is None or results["transients"].empty


@pytest.mark.unit
class TestScoringEdgeCases:
    """Test edge cases in scoring algorithm."""

    def test_score_with_missing_magnitude(self, engine: EnhancedDiscoveryEngineV2) -> None:
        """Test scoring when magnitude is missing."""
        row = pd.Series({"id": "AT2025test", "mag": None, "type": "LRN"})
        score, reasons = engine.calculate_advanced_score(row)

        assert score >= 0.0
        assert isinstance(reasons, list)

    def test_score_with_empty_type(self, engine: EnhancedDiscoveryEngineV2) -> None:
        """Test scoring when type is empty."""
        row = pd.Series({"id": "AT2025test", "mag": 15.0, "type": ""})
        score, reasons = engine.calculate_advanced_score(row)

        assert score >= 0.0

    def test_score_with_unusual_type(self, engine: EnhancedDiscoveryEngineV2) -> None:
        """Test scoring with unusual type."""
        row = pd.Series({"id": "AT2025test", "mag": 15.0, "type": "SLSN"})
        score, reasons = engine.calculate_advanced_score(row)

        assert score > 0.0
        assert any("unusual" in r.lower() for r in reasons)
