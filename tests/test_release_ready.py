"""Release-readiness tests that avoid live network calls."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import astra_discoveries
from astra_discoveries import _render_summary
from src import enhanced_discovery_v2, transient_scraper

SAMPLE_HTML = (Path(__file__).parent / "data" / "rochester_sample.html").read_text(encoding="utf-8")


class _DummyResponse:
    def __init__(self, text: str) -> None:
        self.text = text


def test_version_matches_setup_file() -> None:
    """Ensure the package version matches the installer metadata."""

    setup_path = Path(__file__).resolve().parents[1] / "setup.py"
    match = re.search(r"version=['\"]([^'\"]+)['\"]", setup_path.read_text())
    assert match, "Unable to read version from setup.py"
    setup_version = match.group(1)
    assert astra_discoveries.__version__ == setup_version


def test_scraper_handles_sample_rochester_page(monkeypatch: pytest.MonkeyPatch) -> None:
    """scrape_rochester_sn_page should parse deterministic sample HTML."""

    def fake_get(url: str, timeout: int = 30):  # noqa: ANN001 - signature mirrors requests
        return _DummyResponse(SAMPLE_HTML)

    monkeypatch.setattr(transient_scraper.requests, "get", fake_get)

    df = transient_scraper.scrape_rochester_sn_page()
    assert not df.empty
    assert {"AT2025abao", "AT2025abne"}.issubset(set(df["id"]))


def test_enhanced_engine_scores_rare_objects() -> None:
    """EnhancedDiscoveryEngineV2 should prioritize bright/rare events."""

    engine = enhanced_discovery_v2.EnhancedDiscoveryEngineV2()
    sample = pd.DataFrame(
        [
            {"id": "AT2025abao", "mag": 15.1, "type": "LRN", "source": "Rochester"},
            {"id": "AT2025abne", "mag": 16.0, "type": "unknown", "source": "Rochester"},
            {"id": "SN2025abc", "mag": 18.5, "type": "Ia", "source": "Rochester"},
        ]
    )

    anomalies = engine.find_advanced_anomalies(sample)
    assert anomalies, "Expected at least one anomaly"
    assert anomalies[0]["id"] == "AT2025abao"
    assert anomalies[0]["score"] >= anomalies[-1]["score"]


def test_render_summary_mentions_top_candidate() -> None:
    """The CLI summary should highlight the top anomaly."""

    results = {
        "transients": pd.DataFrame([{"id": "AT2025abao"}]),
        "anomalies": [
            {
                "id": "AT2025abao",
                "mag": 15.1,
                "type": "LRN",
                "score": 8.0,
                "reasons": ["Exceptionally bright", "Rare type"],
            }
        ],
    }

    summary_text = _render_summary(results, mode="advanced")
    assert "AT2025abao" in summary_text
    assert "High-priority anomalies: 1" in summary_text
    assert "Exceptionally bright" in summary_text
