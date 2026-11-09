"""
Tests for the frontend helper modules: summary, availability and ui.

Run from the repository root:
    python -m pytest tests/test_frontend.py -v

These tests do NOT require a trained model or a running Streamlit app.
They verify that the pure helper logic used by app.py behaves correctly.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlp import summary as summary_mod  # noqa: E402
from nlp import ui as ui_mod  # noqa: E402
from nlp.availability import BackendUnavailableError, probe_status  # noqa: E402
from nlp.config import CONTRIBUTION_CSV  # noqa: E402
from nlp.summary import (  # noqa: E402
    batch_progress,
    label_distribution,
    label_progress,
    load_contribution,
    volunteer_progress,
)


# ── summary: verified figures are read, never hardcoded as claims ────────────

def test_summary_reads_live_contribution():
    s = summary_mod.summary(CONTRIBUTION_CSV)
    assert s["exists"] is True
    assert s["total"] == 250
    assert s["language"] == "Lingala"


def test_summary_missing_file_reports_not_exists():
    s = summary_mod.summary("data/does_not_exist.csv")
    assert s["exists"] is False
    assert s["total"] == 0
    assert s["language"] is None


def test_label_distribution_matches_csv():
    df = load_contribution(CONTRIBUTION_CSV)
    counts = label_distribution(df)
    assert len(counts) == 10  # one per taxonomy label
    assert set(counts) == set(summary_mod._known_labels())
    # All labels present and evenly distributed (no label left behind).
    assert len(set(counts.values())) == 1


def test_label_progress_distinguishes_target_from_achieved():
    df = load_contribution(CONTRIBUTION_CSV)
    rows = label_progress(df, summary_mod._known_labels())
    assert len(rows) == 10
    for row in rows:
        assert row["target"] == summary_mod.LABEL_TARGET
        assert row["achieved"] == 25
        assert row["reached"] is True


def test_volunteer_progress_matches_csv():
    df = load_contribution(CONTRIBUTION_CSV)
    rows = volunteer_progress(df)
    assert {r["code"] for r in rows} == set(summary_mod.VOLUNTEER_TARGETS)
    for row in rows:
        assert row["target"] == summary_mod.VOLUNTEER_TARGETS[row["code"]]
        assert row["achieved"] == summary_mod.VOLUNTEER_TARGETS[row["code"]]


def test_batch_progress_uses_achieved_total():
    df = load_contribution(CONTRIBUTION_CSV)
    rows = batch_progress(df)
    assert len(rows) == len(summary_mod.BATCH_MILESTONES)
    for row in rows:
        assert row["achieved"] == len(df)
        assert row["reached"] is True


def test_load_contribution_renames_legacy_intent_header(tmp_path):
    p = tmp_path / "legacy.csv"
    p.write_text("intent,text\nweather_query,Tala mbula lelo.\n", encoding="utf-8")
    df = load_contribution(p)
    assert "label" in df.columns
    assert "intent" not in df.columns
    assert df.iloc[0]["label"] == "weather_query"


# ── availability: never duplicates model-loading logic ───────────────────────

def test_probe_status_reports_unavailable_when_model_missing():
    r = probe_status("intent")
    assert r["available"] is False
    assert r["pack"] is None
    assert r["artefacts"]["model"] == "missing"
    assert "train.py" in r["error"]


def test_probe_raises_when_model_missing():
    with pytest.raises(BackendUnavailableError):
        from nlp.availability import probe
        probe("intent")


# ── ui: pure formatting helpers ──────────────────────────────────────────────

def test_format_probability():
    assert ui_mod.format_probability(0.873) == "87.3%"
    assert ui_mod.format_probability(1.0) == "100.0%"
    assert ui_mod.format_probability(0.0) == "0.0%"


def test_confidence_band_boundaries():
    assert ui_mod.confidence_band(0.95) == "High confidence"
    assert ui_mod.confidence_band(0.8) == "High confidence"
    assert ui_mod.confidence_band(0.7) == "Moderate confidence"
    assert ui_mod.confidence_band(0.5) == "Moderate confidence"
    assert ui_mod.confidence_band(0.4) == "Low confidence"
    assert ui_mod.confidence_band(0.3) == "Low confidence"
    assert ui_mod.confidence_band(0.1) == "Very low confidence"


def test_progress_line_fixed_width():
    line = ui_mod.progress_line(1, 4, width=20)
    assert len(line) == 20
    assert line == "█" * 5 + "░" * 15  # round(0.25 * 20) = 5
    assert ui_mod.progress_line(0, 4, width=20) == "░" * 20


def test_progress_line_clamps_over_target():
    line = ui_mod.progress_line(10, 4, width=20)
    assert line == "█" * 20  # achieved above target still fills the bar


def test_build_disclaimer_per_track():
    assert "calendar" in ui_mod.build_disclaimer("intent").lower()
    assert "slot" in ui_mod.build_disclaimer("semantic").lower()
    assert "emotion" in ui_mod.build_disclaimer("sentiment").lower()