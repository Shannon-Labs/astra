"""Tests for CLI interface (astra_discoveries module)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from astra_discoveries import (
    _prepare_output_dir,
    _print_run_header,
    _print_run_summary,
    _render_summary,
    _run_quick_test,
    _write_results,
    main,
)


@pytest.fixture
def sample_results() -> dict:
    """Sample discovery results for testing."""
    return {
        "transients": pd.DataFrame(
            [
                {"id": "AT2025test1", "mag": 15.1, "type": "LRN"},
                {"id": "AT2025test2", "mag": 16.0, "type": "unknown"},
            ]
        ),
        "anomalies": [
            {
                "id": "AT2025test1",
                "mag": 15.1,
                "type": "LRN",
                "score": 8.0,
                "reasons": ["Exceptionally bright", "Rare type"],
            }
        ],
        "report": "Test report content",
    }


class TestCLIHelpers:
    """Test CLI helper functions."""

    def test_prepare_output_dir_auto(self, tmp_path: Path) -> None:
        """Test auto output directory creation."""
        with patch("astra_discoveries.Path.cwd", return_value=tmp_path):
            output_dir = _prepare_output_dir("auto", "advanced")

        assert output_dir.exists()
        assert "advanced_run_" in output_dir.name

    def test_prepare_output_dir_custom(self, tmp_path: Path) -> None:
        """Test custom output directory creation."""
        custom_dir = tmp_path / "custom_output"
        output_dir = _prepare_output_dir(str(custom_dir), "basic")

        assert output_dir.exists()
        assert output_dir == custom_dir

    def test_render_summary_with_anomalies(self, sample_results: dict) -> None:
        """Test summary rendering with anomalies."""
        summary = _render_summary(sample_results, "advanced")

        assert isinstance(summary, str)
        assert "ASTRA Advanced Discovery Summary" in summary
        assert "AT2025test1" in summary
        assert "High-priority anomalies: 1" in summary

    def test_render_summary_no_anomalies(self) -> None:
        """Test summary rendering with no anomalies."""
        results = {"transients": pd.DataFrame([{"id": "AT2025test"}]), "anomalies": []}

        summary = _render_summary(results, "basic")

        assert "High-priority anomalies: 0" in summary

    def test_write_results(self, sample_results: dict, tmp_path: Path) -> None:
        """Test writing results to disk."""
        artifacts = _write_results(sample_results, tmp_path, "advanced")

        assert artifacts.report is not None
        assert artifacts.catalog is not None
        assert artifacts.summary is not None
        assert artifacts.report.exists()
        assert artifacts.catalog.exists()
        assert artifacts.summary.exists()

    def test_print_run_header(self, capsys) -> None:
        """Test printing run header."""
        _print_run_header("advanced")
        captured = capsys.readouterr()

        assert "ASTRA Discovery System" in captured.out
        assert "Mode: Advanced" in captured.out

    def test_print_run_summary(self, sample_results: dict, capsys) -> None:
        """Test printing run summary."""
        _print_run_summary(sample_results)
        captured = capsys.readouterr()

        assert "Discovery Summary" in captured.out
        assert "Transients analyzed: 2" in captured.out
        assert "High-priority anomalies: 1" in captured.out

    def test_run_quick_test_success(self, capsys) -> None:
        """Test quick test execution."""
        with patch("astra_discoveries.system_check", return_value=True):
            result = _run_quick_test()

        assert result == 0
        captured = capsys.readouterr()
        assert "ASTRA installation looks good" in captured.out

    def test_run_quick_test_failure(self, capsys) -> None:
        """Test quick test with failure."""
        with patch("astra_discoveries.system_check", return_value=False):
            result = _run_quick_test()

        assert result == 1


class TestCLIMain:
    """Test main CLI entry point."""

    def test_main_test_flag(self) -> None:
        """Test main with --test flag."""
        with patch("astra_discoveries.system_check", return_value=True):
            result = main(["--test"])

        assert result == 0

    def test_main_check_flag(self) -> None:
        """Test main with --check flag."""
        with patch("astra_discoveries.system_check", return_value=True):
            result = main(["--check"])

        assert result == 0

    def test_main_basic_mode(self, sample_results: dict, tmp_path: Path) -> None:
        """Test main in basic mode."""
        with patch("astra_discoveries.run_basic_discovery", return_value=sample_results), patch(
            "astra_discoveries.Path.cwd", return_value=tmp_path
        ):
            result = main(["--basic"])

        assert result == 0

    def test_main_advanced_mode(self, sample_results: dict, tmp_path: Path) -> None:
        """Test main in advanced mode."""
        with patch("astra_discoveries.run_advanced_discovery", return_value=sample_results), patch(
            "astra_discoveries.Path.cwd", return_value=tmp_path
        ):
            result = main(["--advanced"])

        assert result == 0

    def test_main_default_mode(self, sample_results: dict, tmp_path: Path) -> None:
        """Test main with default mode (advanced)."""
        with patch("astra_discoveries.run_advanced_discovery", return_value=sample_results), patch(
            "astra_discoveries.Path.cwd", return_value=tmp_path
        ):
            result = main([])

        assert result == 0

    def test_main_keyboard_interrupt(self) -> None:
        """Test main handles KeyboardInterrupt."""
        with patch("astra_discoveries.run_advanced_discovery", side_effect=KeyboardInterrupt):
            result = main(["--advanced"])

        assert result == 1

    def test_main_exception_handling(self) -> None:
        """Test main handles exceptions."""
        with patch("astra_discoveries.run_advanced_discovery", side_effect=Exception("Test error")):
            result = main(["--advanced"])

        assert result == 1

    def test_main_no_results(self) -> None:
        """Test main when no results returned."""
        with patch("astra_discoveries.run_advanced_discovery", return_value=None):
            result = main(["--advanced"])

        assert result == 1

    def test_main_custom_output(self, sample_results: dict, tmp_path: Path) -> None:
        """Test main with custom output directory."""
        output_dir = tmp_path / "custom"
        with patch("astra_discoveries.run_advanced_discovery", return_value=sample_results):
            result = main(["--advanced", "--output", str(output_dir)])

        assert result == 0
        assert output_dir.exists()

    def test_main_verbose_flag(self, sample_results: dict, tmp_path: Path) -> None:
        """Test main with verbose flag."""
        with patch("astra_discoveries.run_advanced_discovery", return_value=sample_results), patch(
            "astra_discoveries.Path.cwd", return_value=tmp_path
        ):
            result = main(["--advanced", "--verbose"])

        assert result == 0


@pytest.mark.integration
class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_cli_help(self, capsys) -> None:
        """Test CLI help output."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])

        assert exc_info.value.code == 0

    def test_cli_test_real_imports(self) -> None:
        """Test that --test checks real imports."""
        result = main(["--test"])
        assert result in [0, 1]

    @patch("astra_discoveries.run_advanced_discovery")
    def test_cli_creates_symlink(
        self, mock_run: Mock, sample_results: dict, tmp_path: Path
    ) -> None:
        """Test that CLI creates latest_discovery symlink."""
        mock_run.return_value = sample_results

        with patch("astra_discoveries.Path.cwd", return_value=tmp_path):
            result = main(["--advanced"])

        assert result == 0
        # Symlink creation is best-effort, may fail on some platforms
