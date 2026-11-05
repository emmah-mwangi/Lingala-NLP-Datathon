"""
Data loading utilities.

Handles CSV loading and model artefact loading.
All file I/O for the application goes through this module so that
path logic stays in one place and errors surface with clear messages.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from nlp.config import model_path, dev_metrics_path, test_predictions_path


class ModelNotTrainedError(FileNotFoundError):
    """Raised when a model artefact does not exist for the requested track."""


class DataLoadError(ValueError):
    """Raised when a CSV cannot be loaded or is structurally invalid."""


def load_model_pack(track: str) -> dict[str, Any]:
    """Load the joblib model pack for *track*.

    Returns the dict saved by train.py:
        {model, dummy, language, practice, track, data_sha256, slot_memory}

    Raises:
        ModelNotTrainedError: if model.joblib does not exist.

    Note: only load .joblib files that your team created and trust.
    """
    path = model_path(track)
    if not path.exists():
        raise ModelNotTrainedError(
            f"No trained model found for track '{track}'. "
            f"Run: python train.py --track {track} --data data/contribution.csv"
        )
    return joblib.load(path)  # noqa: S301 — intentional, team-generated file only


def load_dev_metrics(track: str) -> dict[str, Any] | None:
    """Load dev_metrics.json for *track*, or return None if not yet generated."""
    path = dev_metrics_path(track)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_test_predictions(track: str) -> pd.DataFrame | None:
    """Load test_predictions.csv for *track*, or return None if not yet generated."""
    path = test_predictions_path(track)
    if not path.exists():
        return None
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as exc:
        raise DataLoadError(f"Could not read test predictions: {exc}") from exc


def load_csv(path: Path | str) -> pd.DataFrame:
    """Load a contribution or practice CSV.

    Raises:
        DataLoadError: if the file is missing or cannot be parsed.
    """
    path = Path(path)
    if not path.exists():
        raise DataLoadError(f"CSV not found: {path}")
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as exc:
        raise DataLoadError(f"Could not parse CSV '{path}': {exc}") from exc
