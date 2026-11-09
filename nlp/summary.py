"""
Dataset summary helpers for the Streamlit frontend.

Computes verified figures directly from data/contribution.csv (or any
contribution file). Nothing here is hardcoded as a claim: the "target"
figures are constants describing the *goal* (from TRACKS.md), while the
"achieved" figures are read from the live CSV. The frontend can therefore
show target vs achieved without anyone maintaining a second copy of the
numbers.

This module has no dependency on Streamlit and can be imported and tested
independently of the UI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from nlp.config import CONTRIBUTION_CSV

# ── Goal figures (TRACKS.md / dataset_status.py) ──────────────────────────────
# These describe the TARGET, never a claimed achievement.
LABEL_TARGET = 25
VOLUNTEER_TARGETS: dict[str, int] = {"T07-V1": 17, "T07-V2": 17, "T07-V3": 16}
BATCH_MILESTONES: list[tuple[str, int]] = [
    ("BATCH 1 (Thu 5 Nov)", 80),
    ("BATCH 2 (Fri 6 Nov)", 150),
    ("BATCH 3 (Sat 7 Nov)", 250),
]


def load_contribution(contribution_path: Path | str = CONTRIBUTION_CSV) -> pd.DataFrame:
    """Load a contribution CSV into a DataFrame, or return an empty frame.

    Accepts the legacy ``intent`` column name by renaming it to ``label``.
    """
    path = Path(contribution_path)
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    if "label" not in df.columns and "intent" in df.columns:
        df = df.rename(columns={"intent": "label"})
    return df


def label_distribution(df: pd.DataFrame) -> dict[str, int]:
    if "label" not in df.columns or df.empty:
        return {}
    return df["label"].value_counts().to_dict()


def contributor_distribution(df: pd.DataFrame) -> dict[str, int]:
    if "contributor_code" not in df.columns or df.empty:
        return {}
    return df["contributor_code"].value_counts().to_dict()


def review_coverage(df: pd.DataFrame) -> dict[str, int]:
    if "review_status" not in df.columns or df.empty:
        return {}
    return df["review_status"].value_counts().to_dict()


def split_distribution(df: pd.DataFrame) -> dict[str, int]:
    if "split" not in df.columns or df.empty:
        return {}
    return df["split"].value_counts().to_dict()


def batch_progress(df: pd.DataFrame) -> list[dict[str, Any]]:
    total = len(df)
    return [
        {
            "name": name,
            "target": target,
            "achieved": total,
            "reached": total >= target,
        }
        for name, target in BATCH_MILESTONES
    ]


def label_progress(df: pd.DataFrame, labels: list[str]) -> list[dict[str, Any]]:
    counts = label_distribution(df)
    return [
        {
            "label": label,
            "target": LABEL_TARGET,
            "achieved": counts.get(label, 0),
            "reached": counts.get(label, 0) >= LABEL_TARGET,
        }
        for label in labels
    ]


def volunteer_progress(df: pd.DataFrame) -> list[dict[str, Any]]:
    counts = contributor_distribution(df)
    return [
        {
            "code": code,
            "target": target,
            "achieved": counts.get(code, 0),
            "reached": counts.get(code, 0) >= target,
        }
        for code, target in VOLUNTEER_TARGETS.items()
    ]


def _known_labels() -> list[str]:
    try:
        from core import labels

        return labels("intent")
    except Exception:
        return []


def summary(contribution_path: Path | str = CONTRIBUTION_CSV) -> dict[str, Any]:
    """Return a complete, verified dataset summary dict.

    Keys:
        exists, path, total, language, label_distribution,
        contributor_distribution, review_coverage, split_distribution,
        batch_progress, label_progress, volunteer_progress.
    """
    df = load_contribution(contribution_path)
    return {
        "path": str(contribution_path),
        "exists": not df.empty,
        "total": len(df),
        "language": df["language"].iloc[0]
        if not df.empty and "language" in df.columns
        else None,
        "label_distribution": label_distribution(df),
        "contributor_distribution": contributor_distribution(df),
        "review_coverage": review_coverage(df),
        "split_distribution": split_distribution(df),
        "batch_progress": batch_progress(df),
        "label_progress": label_progress(df, _known_labels()),
        "volunteer_progress": volunteer_progress(df),
    }