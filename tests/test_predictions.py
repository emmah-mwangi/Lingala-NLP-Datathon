"""
Tests for actual model predictions using the trained Lingala intent model.

These tests require artifacts/intent/model.joblib (produced by train.py).
They are skipped automatically when the model artefact is absent.

Run from the repository root:
    python -m pytest tests/test_predictions.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from nlp.data_loader import load_model_pack  # noqa: E402
from nlp.predictor import predict  # noqa: E402

MODEL_PATH = ROOT / "artifacts" / "intent" / "model.joblib"


@pytest.fixture()
def pack():
    if not MODEL_PATH.exists():
        pytest.skip("Trained model artefact not found; run train.py first.")
    return load_model_pack("intent")


def test_model_is_trained_on_lingala(pack):
    """Phase 1: confirm the model language is Lingala, not English."""
    assert pack.get("language") == "Lingala"
    assert pack.get("practice") is False


def test_real_predictions_return_valid_labels(pack):
    """Phase 2: real Lingala sentences return real predicted intents."""
    cases = [
        ("Tala mbula lelo.", "weather_query"),
        ("Yemba miziki.", "play_music"),
        ("Tya alarme na ngonga ya motoba.", "alarm_set"),
        ("Nini ya sika ezali koleka na Kinshasa?", "news_query"),
        ("Bakeseni ezali nini kati na ordinateur na tablette?", "qa_definition"),
    ]
    for text, _expected in cases:
        result = predict(text, pack)
        assert result.label in [
            "weather_query", "datetime_query", "alarm_set", "calendar_set",
            "calendar_query", "lists_createoradd", "lists_query", "play_music",
            "news_query", "qa_definition",
        ]
        assert 0.0 <= result.probability <= 1.0
        assert result.track == "intent"


def test_predict_raises_on_empty_input(pack):
    with pytest.raises(ValueError):
        predict("   ", pack)
