"""
Module import and unit tests.

Run from the repository root:
    python -m pytest tests/ -v

These tests do NOT require a trained model. They verify:
  - All nlp package modules import cleanly.
  - Config paths resolve to the correct locations.
  - Utility functions return correct output.
  - Predictor raises ValueError on empty input (contract test).
  - data_loader raises ModelNotTrainedError for a missing model.

Tests that require artifacts/intent/model.joblib are skipped automatically
until Tatyana's pipeline has run.
"""

import sys
from pathlib import Path

import pytest

# Ensure the repo root is on sys.path when running from any working directory.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Import tests ──────────────────────────────────────────────────────────────

def test_import_config():
    from nlp import config  # noqa: F401


def test_import_data_loader():
    from nlp import data_loader  # noqa: F401


def test_import_predictor():
    from nlp import predictor  # noqa: F401


def test_import_utils():
    from nlp import utils  # noqa: F401


def test_import_core():
    """core.py is Tatyana's module; verify it is importable."""
    import core  # noqa: F401


def test_import_validate():
    """validate.py is Tatyana's module; verify it is importable."""
    import validate  # noqa: F401


# ── Config tests ──────────────────────────────────────────────────────────────

def test_config_root_exists():
    from nlp.config import ROOT
    assert ROOT.is_dir()


def test_config_data_dir_exists():
    from nlp.config import DATA_DIR
    assert DATA_DIR.is_dir()


def test_config_practice_paths_exist():
    from nlp.config import PRACTICE_DATA
    for track, path in PRACTICE_DATA.items():
        assert path.exists(), f"Practice CSV missing for track '{track}': {path}"


def test_config_model_path_shape():
    from nlp.config import model_path
    p = model_path("intent")
    assert p.name == "model.joblib"
    assert p.parent.name == "intent"


def test_config_supported_tracks():
    from nlp.config import SUPPORTED_TRACKS
    assert set(SUPPORTED_TRACKS) == {"intent", "sentiment", "semantic"}


# ── Utils tests ───────────────────────────────────────────────────────────────

def test_normalise_text_collapses_whitespace():
    from nlp.utils import normalise_text
    assert normalise_text("  hello   world  ") == "hello world"


def test_normalise_text_nfc():
    from nlp.utils import normalise_text
    # Decomposed 'é' (e + combining acute) should become composed 'é'.
    decomposed = "e\u0301"
    assert normalise_text(decomposed) == "\xe9"


def test_format_probability():
    from nlp.utils import format_probability
    assert format_probability(0.873) == "87.3%"
    assert format_probability(1.0) == "100.0%"
    assert format_probability(0.0) == "0.0%"


def test_bar_chart_str_length():
    from nlp.utils import bar_chart_str
    result = bar_chart_str(0.5, width=20)
    assert len(result) == 20


def test_bar_chart_str_full():
    from nlp.utils import bar_chart_str
    assert bar_chart_str(1.0, width=10) == "█" * 10


# ── data_loader tests ─────────────────────────────────────────────────────────

def test_load_model_pack_raises_when_missing():
    from nlp.data_loader import ModelNotTrainedError, load_model_pack
    with pytest.raises(ModelNotTrainedError):
        load_model_pack("intent")


def test_load_dev_metrics_returns_none_when_missing():
    from nlp.data_loader import load_dev_metrics
    result = load_dev_metrics("intent")
    assert result is None


def test_load_test_predictions_returns_none_when_missing():
    from nlp.data_loader import load_test_predictions
    result = load_test_predictions("intent")
    assert result is None


def test_load_csv_raises_on_missing_file():
    from nlp.data_loader import DataLoadError, load_csv
    with pytest.raises(DataLoadError):
        load_csv("data/does_not_exist.csv")


def test_load_csv_practice_intent():
    from nlp.config import PRACTICE_DATA
    from nlp.data_loader import load_csv
    df = load_csv(PRACTICE_DATA["intent"])
    assert len(df) == 100
    assert "text" in df.columns
    assert "label" in df.columns


# ── predictor contract tests (no model required) ──────────────────────────────

def test_predict_raises_on_empty_text():
    from nlp.predictor import predict
    # A minimal fake pack that satisfies the interface contract.
    class _FakeModel:
        def predict(self, X):
            return ["weather_query"]
        def predict_proba(self, X):
            return [[0.9, 0.1]]

    fake_pack = {
        "model": _FakeModel(),
        "track": "intent",
        "slot_memory": {},
    }
    with pytest.raises(ValueError):
        predict("   ", fake_pack)


def test_predict_returns_result_shape():
    from nlp.predictor import PredictionResult, predict

    class _FakeModel:
        def predict(self, X):
            return ["weather_query"]
        def predict_proba(self, X):
            return [[0.85, 0.15]]

    fake_pack = {
        "model": _FakeModel(),
        "track": "intent",
        "slot_memory": {},
    }
    result = predict("Hali ya hewa leo?", fake_pack)
    assert isinstance(result, PredictionResult)
    assert result.label == "weather_query"
    assert 0.0 <= result.probability <= 1.0
    assert result.slots == []
    assert result.track == "intent"
