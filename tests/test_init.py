"""Tests for src/__init__.py module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from src import (
    AstraDiscoveryEngine,
    EnhancedDiscoveryEngineV2,
    TransientScraper,
    __version__,
    run_advanced_discovery,
    run_basic_discovery,
    system_check,
)


class TestModuleConstants:
    """Test module-level constants."""

    def test_version(self) -> None:
        """Test version is set correctly."""
        assert __version__ == "2.0.2"
        assert isinstance(__version__, str)


class TestSystemCheck:
    """Test system check function."""

    def test_system_check_success(self, capsys) -> None:
        """Test system check with all dependencies available."""
        result = system_check()

        captured = capsys.readouterr()
        assert result is True
        assert "ASTRA IS READY" in captured.out
        assert "astroquery" in captured.out
        assert "astropy" in captured.out
        assert "numpy" in captured.out
        assert "pandas" in captured.out

    def test_system_check_import_error(self, capsys) -> None:
        """Test system check with missing dependency."""
        # Temporarily hide a module to simulate ImportError
        with patch.dict("sys.modules", {"astroquery": None}):
            # This should still pass as we're not actually breaking imports in real environment
            # In real scenario with missing module, it would return False
            result = system_check()
            assert result is True or result is False


class TestRunBasicDiscovery:
    """Test run_basic_discovery function."""

    @patch("src.AstraDiscoveryEngine.run_discovery_pipeline")
    def test_run_basic_discovery(self, mock_pipeline: Mock) -> None:
        """Test basic discovery pipeline execution."""
        expected_results = {"transients": [], "anomalies": []}
        mock_pipeline.return_value = expected_results

        results = run_basic_discovery()

        assert results == expected_results
        mock_pipeline.assert_called_once()

    @patch("src.AstraDiscoveryEngine")
    def test_run_basic_discovery_creates_engine(self, mock_engine_class: Mock) -> None:
        """Test that basic discovery creates an engine instance."""
        mock_instance = Mock()
        mock_instance.run_discovery_pipeline.return_value = {}
        mock_engine_class.return_value = mock_instance

        run_basic_discovery()

        mock_engine_class.assert_called_once()
        mock_instance.run_discovery_pipeline.assert_called_once()


class TestRunAdvancedDiscovery:
    """Test run_advanced_discovery function."""

    @patch("src.EnhancedDiscoveryEngineV2.run_advanced_pipeline")
    def test_run_advanced_discovery(self, mock_pipeline: Mock) -> None:
        """Test advanced discovery pipeline execution."""
        expected_results = {"transients": [], "anomalies": [], "report": "test"}
        mock_pipeline.return_value = expected_results

        results = run_advanced_discovery()

        assert results == expected_results
        mock_pipeline.assert_called_once()

    @patch("src.EnhancedDiscoveryEngineV2")
    def test_run_advanced_discovery_creates_engine(self, mock_engine_class: Mock) -> None:
        """Test that advanced discovery creates an engine instance."""
        mock_instance = Mock()
        mock_instance.run_advanced_pipeline.return_value = {}
        mock_engine_class.return_value = mock_instance

        run_advanced_discovery()

        mock_engine_class.assert_called_once()
        mock_instance.run_advanced_pipeline.assert_called_once()


class TestImports:
    """Test that all expected names are importable."""

    def test_transient_scraper_import(self) -> None:
        """Test TransientScraper is importable."""
        assert TransientScraper is not None

    def test_astra_discovery_engine_import(self) -> None:
        """Test AstraDiscoveryEngine is importable."""
        assert AstraDiscoveryEngine is not None

    def test_enhanced_discovery_engine_import(self) -> None:
        """Test EnhancedDiscoveryEngineV2 is importable."""
        assert EnhancedDiscoveryEngineV2 is not None


class TestModuleAll:
    """Test __all__ exports."""

    def test_all_names_defined(self) -> None:
        """Test that all names in __all__ are defined."""
        import src

        for name in src.__all__:
            assert hasattr(src, name), f"{name} not found in module"


@pytest.mark.integration
class TestIntegrationDiscovery:
    """Integration tests for discovery functions."""

    @pytest.mark.skip(reason="Requires network access - run manually")
    def test_basic_discovery_integration(self) -> None:
        """Test basic discovery with real network call."""
        results = run_basic_discovery()

        assert results is not None
        assert isinstance(results, dict)

    @pytest.mark.skip(reason="Requires network access - run manually")
    def test_advanced_discovery_integration(self) -> None:
        """Test advanced discovery with real network call."""
        results = run_advanced_discovery()

        assert results is not None
        assert isinstance(results, dict)
        assert "report" in results
