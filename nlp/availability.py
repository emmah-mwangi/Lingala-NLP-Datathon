"""
Backend availability probe for the Streamlit frontend.

Wraps data_loader.load_model_pack() so the UI has one stable, testable
function to ask "is the model ready for this track?". The probe never
duplicates model-loading logic; it only decides how to present the result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from nlp.config import artifact_dir
from nlp.data_loader import ModelNotTrainedError, load_model_pack


class BackendUnavailableError(Exception):
    """Raised when the model artefacts for a track are missing."""


def probe(track: str) -> dict[str, Any]:
    """Check whether the backend is ready for *track*.

    "Ready for prediction" means the trained model artefact exists. The
    evaluation artefacts (dev/test metrics and predictions) are reported
    separately because they are produced later in the workflow by
    evaluate.py; their absence does not block prediction.

    Returns a dict describing availability:
        available: bool
        artefacts: dict[str, str]  path -> "present" | "missing"
        error: str | None

    Raises:
        BackendUnavailableError: if the model artefact is absent.
    """
    artefact_dir = artifact_dir(track)
    expected = {
        "model": artefact_dir / "model.joblib",
        "dev_metrics": artefact_dir / "dev_metrics.json",
        "test_metrics": artefact_dir / "test_metrics.json",
        "test_predictions": artefact_dir / "test_predictions.csv",
    }
    status = {name: ("present" if path.exists() else "missing") for name, path in expected.items()}

    if status["model"] == "missing":
        raise BackendUnavailableError(
            f"Backend not ready for track '{track}': missing model artefact. "
            f"Run: python train.py --track {track} --data data/contribution.csv"
        )

    pack = load_model_pack(track)
    return {
        "available": True,
        "artefacts": status,
        "error": None,
        "pack": pack,
    }


def _artefact_status(track: str) -> dict[str, str]:
    artefact_dir = artifact_dir(track)
    expected = {
        "model": artefact_dir / "model.joblib",
        "dev_metrics": artefact_dir / "dev_metrics.json",
        "test_metrics": artefact_dir / "test_metrics.json",
        "test_predictions": artefact_dir / "test_predictions.csv",
    }
    return {
        name: ("present" if path.exists() else "missing")
        for name, path in expected.items()
    }


def probe_status(track: str) -> dict[str, Any]:
    """Non-raising variant: returns the same dict with available=False instead."""
    try:
        return probe(track)
    except BackendUnavailableError as exc:
        return {
            "available": False,
            "artefacts": _artefact_status(track),
            "error": str(exc),
            "pack": None,
        }